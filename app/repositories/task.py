from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, Column, and_
from sqlalchemy.sql.expression import Select
import logging

from ..models.task import Task, TaskStatus
from ..schemas.task import TaskFilter

logger = logging.getLogger(__name__)

class TaskRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self, task_id: int) -> Optional[Task]:
        stmt = (
            select(Task)
            .options(
                joinedload(Task.project),
                joinedload(Task.assignee),
                joinedload(Task.author)
            )
            .where(Task.id == task_id)
        )
        return self.db.scalar(stmt)

    def get_by_project(self, project_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        stmt = select(Task).where(Task.project_id == project_id).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        stmt = select(Task).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, db_task: Task, task_update_data: dict) -> Task:
        for key, value in task_update_data.items():
            setattr(db_task, key, value)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def delete(self, db_task: Task) -> None:
        self.db.delete(db_task)
        self.db.commit()

    def get_tasks(self, filters: TaskFilter) -> List[Task]:
        stmt = select(Task).options(
            joinedload(Task.project),
            joinedload(Task.assignee),
            joinedload(Task.author)
        )
        conditions = []
        filter_params = filters.model_dump(exclude_unset=True)

        filter_mapping: Dict[str, Dict[str, Any]] = {
            "project_id": {"attribute": Task.project_id, "operator": "=="},
            "title": {"attribute": Task.title, "operator": "ilike", "format": "%{}%"},
            "status": {"attribute": Task.status, "operator": "=="},
            "created_at_start": {"attribute": Task.created_at, "operator": ">="},
            "created_at_end": {"attribute": Task.created_at, "operator": "<="},
            "author_id": {"attribute": Task.author_id, "operator": "=="},
        }

        for filter_name, filter_value in filter_params.items():
            if filter_value is not None and filter_name in filter_mapping:
                mapping = filter_mapping[filter_name]
                attribute = mapping["attribute"]
                operator = mapping["operator"]
                value_to_use = filter_value

                if "format" in mapping:
                    value_to_use = mapping["format"].format(filter_value)

                if operator == "==":
                    conditions.append(attribute == value_to_use)
                elif operator == "ilike":
                    conditions.append(attribute.ilike(value_to_use))
                elif operator == ">=":
                    conditions.append(attribute >= value_to_use)
                elif operator == "<=":
                    conditions.append(attribute <= value_to_use)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        compiled_stmt = stmt.compile(compile_kwargs={"literal_binds": True})
        logger.info(f"SQL Query: {compiled_stmt}")

        results = self.db.execute(stmt).scalars().all()
        logger.info(f"Query Results: {results}")
        return results