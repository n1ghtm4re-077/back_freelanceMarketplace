import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from jose import jwt
from sqlalchemy.orm import Session

from backend.app.models import Chat, Task, Message, User
from backend.app.schemas import ChatCreate, MessageCreate, MessageResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db
from backend.app.models import Notification
from backend.app.routes.notifications import create_notification

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/", response_model=dict)
def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Создание чата между участниками задачи
    """
    task = db.query(Task).filter(Task.task_id == chat_data.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.user_type == "freelancer":
        user2_id = task.employer_id
    elif current_user.user_type == "employer":
        user2_id = task.freelancer_id
    else:
        raise HTTPException(status_code=403, detail="Unknown user type")

    if current_user.user_id == user2_id:
        raise HTTPException(status_code=400, detail="You can't create a chat with yourself")

    # Проверяем, есть ли уже такой чат
    existing_chat = db.query(Chat).filter(
        ((Chat.user1_id == current_user.user_id) & (Chat.user2_id == user2_id)) |
        ((Chat.user1_id == user2_id) & (Chat.user2_id == current_user.user_id)),
        Chat.task_id == chat_data.task_id
    ).first()

    if existing_chat:
        return {"message": "Chat already exists", "chat_id": existing_chat.chat_id}

    # Создаем новый чат
    new_chat = Chat(**chat_data.dict(), user1_id=current_user.user_id, user2_id=user2_id)
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return {"message": "Chat created", "chat_id": new_chat.chat_id}


@router.post("/{chat_id}/messages", response_model=MessageResponse)
def send_message(
    chat_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Отправка сообщения в чат
    """
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if current_user.user_id not in [chat.user1_id, chat.user2_id]:
        raise HTTPException(status_code=403, detail="You are not a participant of this chat")

    new_message = Message(chat_id=chat_id, sender_id=current_user.user_id, content=message_data.content)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    # Уведомляем другого пользователя
    other_user_id = chat.user1_id if chat.user2_id == current_user.user_id else chat.user2_id
    create_notification(
        db=db,
        notification_data=dict(
            user_id=other_user_id,
            message=f"Новое сообщение от {current_user.first_name} в чате",
            related_entity_type="chat",
            related_entity_id=new_message.message_id
        )
    )

    return new_message


@router.get("/{task_id}/messages", response_model=list[MessageResponse])
def get_messages_by_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Получить все сообщения по задаче
    """
    chat = db.query(Chat).filter(Chat.task_id == task_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="No chat for this task")

    if current_user.user_id not in [chat.user1_id, chat.user2_id]:
        raise HTTPException(status_code=403, detail="You are not a participant of this chat")

    messages = db.query(Message).filter(Message.chat_id == chat.chat_id).all()
    return messages


@router.websocket("/ws/{chat_id}/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Подключение к чату через WebSocket
    """
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        email: str = payload.get("sub")
        if email is None:
            await websocket.close(code=4000)
            return

        current_user = db.query(User).filter(User.email == email).first()
        if not current_user:
            await websocket.close(code=4000)
            return

        chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
        if not chat or current_user.user_id not in [chat.user1_id, chat.user2_id]:
            await websocket.close(code=4000)
            return

        await websocket.accept()

        while True:
            data = await websocket.receive_text()
            new_message = Message(chat_id=chat_id, sender_id=current_user.user_id, content=data)
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            await websocket.send_json({
                "sender_id": current_user.user_id,
                "content": data,
                "created_at": datetime.now().isoformat(),
                "is_read": False
            })

    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=4000)