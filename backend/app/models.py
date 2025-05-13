from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    Numeric, ForeignKey, Text, Date, CheckConstraint,
    ARRAY, UniqueConstraint
)
from sqlalchemy import func
from backend import Base

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    user_type = Column(String(20), nullable=False)
    last_online = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(user_type.in_(['freelancer', 'employer']), name='check_user_type'),
    )

class FreelancerProfile(Base):
    __tablename__ = 'freelancer_profiles'

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    skills = Column(ARRAY(Text))
    rating = Column(Numeric(3, 2), default=0.00)
    positive_reviews = Column(Integer, default=0)
    negative_reviews = Column(Integer, default=0)
    portfolio_links = Column(ARRAY(Text))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EmployerProfile(Base):
    __tablename__ = 'employer_profiles'

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    rating = Column(Numeric(3, 2), default=0.00)
    positive_reviews = Column(Integer, default=0)
    negative_reviews = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Category(Base):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Numeric(12, 2))
    budget_type = Column(String(20))
    min_budget = Column(Numeric(12, 2))
    max_budget = Column(Numeric(12, 2))
    category_id = Column(Integer, ForeignKey('categories.category_id', ondelete='SET NULL'))
    deadline = Column(Date)
    requirements = Column(Text)
    status = Column(String(20), default='open')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(budget_type.in_(['fixed', 'range']), name='check_budget_type'),
        CheckConstraint(status.in_(['open', 'in_progress', 'completed', 'closed']), name='check_task_status'),
    )

class Bid(Base):
    __tablename__ = 'bids'

    bid_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id', ondelete='CASCADE'), nullable=False)
    freelancer_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    comment = Column(Text)
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'accepted', 'rejected']), name='check_bid_status'),
    )

class AssignedTask(Base):
    __tablename__ = 'assigned_tasks'

    assignment_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id', ondelete='CASCADE'), unique=True, nullable=False)
    freelancer_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    employer_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    agreed_amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), default='in_progress')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(status.in_(['in_progress', 'completed', 'disputed']), name='check_assignment_status'),
    )

class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id', ondelete='CASCADE'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    reviewed_user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    is_positive = Column(Boolean)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(rating.between(1, 5), name='check_rating_range'),
    )

class Chat(Base):
    __tablename__ = 'chats'

    chat_id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.task_id', ondelete='SET NULL'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('user1_id', 'user2_id', 'task_id', name='unique_chat_participants'),
        CheckConstraint('user1_id <> user2_id', name='check_different_users'),
    )

class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.chat_id', ondelete='CASCADE'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class Notification(Base):
    __tablename__ = 'notifications'

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    related_entity_type = Column(String(50))
    related_entity_id = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())