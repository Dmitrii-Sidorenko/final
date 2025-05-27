from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import select, Column
from sqlalchemy.sql.expression import Select

from ..models import category as category_model
from ..schemas.category import CategoryFilter

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, category_id: int) -> Optional[category_model.Category]:
        stmt = select(category_model.Category).where(category_model.Category.id == category_id)
        return self.db.scalar(stmt)

    def _apply_filters(self, stmt: Select[tuple[category_model.Category]], filters: Optional[CategoryFilter]) -> Select[tuple[category_model.Category]]:
        if filters:
            if filters.name:
                stmt = stmt.where(category_model.Category.name.ilike(f"%{filters.name}%"))
            if filters.color:
                stmt = stmt.where(category_model.Category.color == filters.color)
            if filters.owner_id is not None:
                stmt = stmt.where(category_model.Category.owner_id == filters.owner_id)
        return stmt

    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100, filters: Optional[CategoryFilter] = None) -> List[category_model.Category]:
        stmt = select(category_model.Category).where(category_model.Category.owner_id == owner_id)
        stmt = self._apply_filters(stmt, filters)
        return self.db.scalars(stmt.offset(skip).limit(limit)).all()

    def get_all(self, skip: int = 0, limit: int = 100, filters: Optional[CategoryFilter] = None) -> List[category_model.Category]:
        stmt = select(category_model.Category)
        stmt = self._apply_filters(stmt, filters)
        return self.db.scalars(stmt.offset(skip).limit(limit)).all()

    def create(self, category: category_model.Category) -> category_model.Category:
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, db_category: category_model.Category, update_data: dict) -> category_model.Category:
        for key, value in update_data.items():
            setattr(db_category, key, value)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete(self, db_category: category_model.Category) -> None:
        self.db.delete(db_category)
        self.db.commit()
        return None