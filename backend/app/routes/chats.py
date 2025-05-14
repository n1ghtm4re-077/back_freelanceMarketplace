from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.models import Chat, Message, User, Task, Notification
from backend.app.schemas import ChatCreate, ChatResponse, MessageCreate, MessageResponse
from backend.app.auth import get_current_user
from backend.app.database import get_db

router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/", response_model=ChatResponse)
def create_chat(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новый чат между двумя пользователями.
    Чат связан с конкретной задачей.
    """
    # Проверяем, что пользователь не создаёт чат сам с собой
    if chat_data.user1_id == chat_data.user2_id:
        raise HTTPException(status_code=400, detail="You cannot create a chat with yourself")

    # Проверяем, существует ли оба пользователя
    user1 = db.query(User).filter(User.user_id == chat_data.user1_id).first()
    user2 = db.query(User).filter(User.user_id == chat_data.user2_id).first()

    if not user1 or not user2:
        raise HTTPException(status_code=404, detail="One of the users not found")

    # Проверяем, существует ли задача
    task = db.query(Task).filter(Task.task_id == chat_data.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверяем, является ли пользователь участником задачи
    if current_user.user_id not in [task.employer_id, task.freelancer_id]:
        raise HTTPException(status_code=403, detail="You are not a participant of this task")

    # Проверяем, есть ли уже такой чат
    existing_chat = db.query(Chat).filter(
        ((Chat.user1_id == chat_data.user1_id) & (Chat.user2_id == chat_data.user2_id)) |
        ((Chat.user1_id == chat_data.user2_id) & (Chat.user2_id == chat_data.user1_id)),
        Chat.task_id == chat_data.task_id
    ).first()

    if existing_chat:
        return {"message": "Chat already exists", "chat_id": existing_chat.chat_id}

    # Создаем новый чат
    new_chat = Chat(
        user1_id=chat_data.user1_id,
        user2_id=chat_data.user2_id,
        task_id=chat_data.task_id
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    return new_chat


@router.post("/{chat_id}/messages", response_model=MessageResponse)
def send_message(
    chat_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отправить сообщение в чат
    """

    # Проверяем, существует ли чат
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Проверяем, является ли пользователь участником чата
    if current_user.user_id not in [chat.user1_id, chat.user2_id]:
        raise HTTPException(status_code=403, detail="You are not a participant of this chat")

    # Создаем новое сообщение
    new_message = Message(
        chat_id=chat_id,
        sender_id=current_user.user_id,
        content=message_data.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    # Создаем уведомление для другого участника чата
    other_user_id = chat.user1_id if chat.user2_id == current_user.user_id else chat.user2_id
    new_notification = Notification(
        user_id=other_user_id,
        message=f"Новое сообщение от {current_user.first_name} в чате по задаче",
        is_read=False
    )
    db.add(new_notification)
    db.commit()

    return new_message


@router.get("/{task_id}/messages", response_model=list[MessageResponse])
def get_messages(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить все сообщения из чата, связанные с задачей
    """

    # Проверяем, существует ли задача
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Проверяем, является ли пользователь участником задачи
    if current_user.user_id not in [task.employer_id, task.freelancer_id]:
        raise HTTPException(status_code=403, detail="You are not a participant of this task")

    # Получаем чат, связанный с задачей
    chat = db.query(Chat).filter(Chat.task_id == task_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="No chat found for this task")

    # Получаем сообщения
    messages = db.query(Message).filter(Message.chat_id == chat.chat_id).all()
    return messages


@router.get("/me", response_model=list[dict])
def get_my_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список всех чатов текущего пользователя
    """
    chats = db.query(Chat).join(Task).filter(
        ((Chat.user1_id == current_user.user_id) | (Chat.user2_id == current_user.user_id))
    ).all()

    result = []
    for chat in chats:
        other_user_id = chat.user1_id if chat.user2_id == current_user.user_id else chat.user2_id
        other_user = db.query(User).filter(User.user_id == other_user_id).first()

        result.append({
            "chat_id": chat.chat_id,
            "with_user": {
                "user_id": other_user.user_id,
                "email": other_user.email,
                "first_name": other_user.first_name,
                "last_name": other_user.last_name,
                "user_type": other_user.user_type
            },
            "task_id": chat.task_id,
            "created_at": chat.created_at
        })

    return result


@router.put("/{chat_id}/messages/{message_id}")
def edit_message(
    chat_id: int,
    message_id: int,
    new_content: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Редактировать собственное сообщение
    """

    message = db.query(Message).filter(
        Message.message_id == message_id,
        Message.chat_id == chat_id,
        Message.sender_id == current_user.user_id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.content = new_content
    db.commit()
    db.refresh(message)

    return message


@router.delete("/{chat_id}/messages/{message_id}")
def delete_message(
    chat_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить сообщение
    """

    message = db.query(Message).filter(
        Message.message_id == message_id,
        Message.chat_id == chat_id,
        Message.sender_id == current_user.user_id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(message)
    db.commit()

    return {"message": "Message deleted"}