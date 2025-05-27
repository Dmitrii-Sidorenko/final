from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, func
from sqlalchemy.orm import relationship
from .base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    color = Column(String, nullable=True)

    owner = relationship("User", back_populates="categories", lazy="selectin")
    projects = relationship("Project", back_populates="category", lazy="selectin")