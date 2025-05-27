from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .photo import Photo  # Прямой импорт модели Photo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .category import Category
    from .project import Project
    from .task import Task
    from .subtask import SubTask
    from .reset_password_token import ResetPasswordToken
    # from .photo import Photo

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String(50), nullable=True)
    avatar = Column(Integer, ForeignKey("photos.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    categories = relationship("Category", back_populates="owner")
    projects = relationship("Project", back_populates="owner")
    created_tasks = relationship("Task", back_populates="author", foreign_keys="Task.author_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    created_subtasks = relationship(
        "SubTask",
        back_populates="author",
        foreign_keys="SubTask.author_id"
    )
    assigned_subtasks = relationship(
        "SubTask",
        back_populates="assignee",
        foreign_keys="SubTask.assignee_id"
    )
    owned_subtasks = relationship(
        "SubTask",
        back_populates="owner",
        foreign_keys="SubTask.owner_id"
    )
    reset_password_tokens = relationship(
        "ResetPasswordToken",
        back_populates="user",
        foreign_keys="ResetPasswordToken.user_id"
    )
    participated_projects = relationship("Project", secondary="project_participants", back_populates="participants")
    photo = relationship("Photo", foreign_keys=[avatar], backref="users_with_avatar")
