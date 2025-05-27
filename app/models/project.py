from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Table
from sqlalchemy.orm import relationship
from .base import Base

project_participants = Table(
    "project_participants",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id")),
    Column("user_id", Integer, ForeignKey("users.id")),
)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    icon_id = Column(Integer, ForeignKey("photos.id"), nullable=True)

    owner = relationship("User", back_populates="projects", foreign_keys=[owner_id])
    tasks = relationship("Task", back_populates="project", lazy="selectin")
    category = relationship("Category", back_populates="projects")
    icon = relationship("Photo", back_populates="projects")
    participants = relationship("User", secondary=project_participants, back_populates="participated_projects")