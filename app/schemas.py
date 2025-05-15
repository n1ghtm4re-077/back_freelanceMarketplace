from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

class UserTypeEnum(str, Enum):
    freelancer = "freelancer"
    employer = "employer"

class BudgetTypeEnum(str, Enum):
    fixed = "fixed"
    range = "range"

class TaskStatusEnum(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    closed = "closed"

class BidStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class AssignmentStatusEnum(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    disputed = "disputed"


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    user_type: UserTypeEnum

class FreelancerProfileBase(BaseModel):
    skills: Optional[List[str]] = []
    portfolio_links: Optional[List[str]] = []

class EmployerProfileBase(BaseModel):
    pass  # Можно расширить позже

class TaskBase(BaseModel):
    title: str
    description: str
    budget_type: Optional[BudgetTypeEnum] = None
    budget: Optional[float] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    deadline: Optional[datetime] = None
    requirements: Optional[str] = None
    category_id: Optional[int] = None
    status: TaskStatusEnum = TaskStatusEnum.open

class BidBase(BaseModel):
    task_id: int
    amount: float
    comment: Optional[str] = None

class ChatBase(BaseModel):
    user1_id: int
    user2_id: int
    task_id: Optional[int] = None

class MessageBase(BaseModel):
    chat_id: int
    content: str


class UserCreate(UserBase):
    password: str

class FreelancerProfileCreate(FreelancerProfileBase):
    user_id: int

class EmployerProfileCreate(EmployerProfileBase):
    user_id: int

class TaskCreate(TaskBase):
    title: str
    description: str
    budget_type: Optional[BudgetTypeEnum] = None
    budget: Optional[float] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    deadline: Optional[datetime] = None
    requirements: Optional[str] = None
    category_id: Optional[int] = None
    status: TaskStatusEnum = TaskStatusEnum.open

class BidCreate(BidBase):
    pass  # freelancer_id будет браться из текущего пользователя через auth

class ChatCreate(ChatBase):
    pass

class MessageCreate(MessageBase):
    pass  # sender_id берётся из JWT токена

class ReviewCreate(BaseModel):
    task_id: int
    reviewed_user_id: int
    rating: int
    comment: Optional[str] = None
    is_positive: bool

class NotificationCreate(BaseModel):
    user_id: int
    message: str
    related_entity_type: str
    related_entity_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget_type: Optional[BudgetTypeEnum] = None
    budget: Optional[float] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    deadline: Optional[datetime] = None
    requirements: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[TaskStatusEnum] = None

class BidUpdate(BaseModel):
    status: BidStatusEnum

class AssignedTaskUpdate(BaseModel):
    status: AssignmentStatusEnum

class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    is_positive: Optional[bool] = None

class NotificationUpdate(BaseModel):
    is_read: bool


class UserResponse(UserBase):
    user_id: int
    email: str
    first_name: str
    last_name: str
    user_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_online: Optional[datetime] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True

class FreelancerProfileResponse(FreelancerProfileBase):
    profile_id: int
    user_id: int
    rating: float
    positive_reviews: int
    negative_reviews: int
    portfolio_links: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class EmployerProfileResponse(EmployerProfileBase):
    profile_id: int
    user_id: int
    rating: float
    positive_reviews: int
    negative_reviews: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class CategoryResponse(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class TaskResponse(TaskBase):
    task_id: int
    title: str
    description: str
    budget_type: Optional[str] = None
    budget: Optional[float] = None
    min_budget: Optional[float] = None
    max_budget: Optional[float] = None
    deadline: Optional[datetime] = None
    requirements: Optional[str] = None
    category_id: Optional[int] = None
    status: str
    employer_id: int
    freelancer_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class BidResponse(BidBase):
    bid_id: int
    status: BidStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AssignedTaskResponse(BaseModel):
    assignment_id: int
    task_id: int
    freelancer_id: int
    employer_id: int
    agreed_amount: float
    status: AssignmentStatusEnum
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ChatResponse(ChatBase):
    chat_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class MessageResponse(MessageBase):
    message_id: int
    sender_id: int
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True

class ReviewResponse(BaseModel):
    review_id: int
    task_id: int
    reviewer_id: int
    reviewed_user_id: int
    rating: int
    comment: Optional[str] = None
    is_positive: bool
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationResponse(BaseModel):
    notification_id: int
    user_id: int
    message: str
    is_read: bool
    related_entity_type: str
    related_entity_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None