from sqlalchemy.orm import Session, selectinload
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.sql.expression import Select
import logging

from ..models.subtask import SubTask, SubTaskStatus
from ..schemas.subtask import SubtaskFilter

logger = logging.getLogger(__name__)

class SubtaskRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self, subtask_id: int) -> Optional[SubTask]:
        stmt = (
            select(SubTask)
            .where(SubTask.id == subtask_id)
            .options(selectinload(SubTask.author), selectinload(SubTask.assignee))
        )
        return self.db.scalar(stmt)

    def _apply_filters(self, stmt: Select[tuple[SubTask]], filters: Optional[SubtaskFilter]) -> Select[tuple[SubTask]]:
        if filters:
            conditions = []
            filter_params = filters.model_dump(exclude_unset=True)
            filter_mapping: Dict[str, Dict[str, Any]] = {
                "title": {"attribute": SubTask.title, "operator": "ilike", "format": "%{}%"},
                "status": {"attribute": SubTask.status, "operator": "=="},
                "assignee_id": {"attribute": SubTask.assignee_id, "operator": "=="},
                "author_id": {"attribute": SubTask.author_id, "operator": "=="},
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
            if conditions:
                stmt = stmt.where(and_(*conditions))
        return stmt

    def get_by_task(self, task_id: int, skip: int = 0, limit: int = 100, filters: Optional[SubtaskFilter] = None) -> List[SubTask]:
        stmt = (
            select(SubTask)
            .where(SubTask.task_id == task_id)
            .options(selectinload(SubTask.author), selectinload(SubTask.assignee))
        )
        stmt = self._apply_filters(stmt, filters)
        compiled_stmt = stmt.compile(compile_kwargs={"literal_binds": True})
        logger.info(f"SQL Query: {compiled_stmt}")
        results = self.db.scalars(stmt.offset(skip).limit(limit)).all()
        logger.info(f"Query Results: {results}")
        return results

    def get_all(self, skip: int = 0, limit: int = 100, filters: Optional[SubtaskFilter] = None) -> List[SubTask]:
        stmt = select(SubTask).options(selectinload(SubTask.author), selectinload(SubTask.assignee))
        stmt = self._apply_filters(stmt, filters)
        compiled_stmt = stmt.compile(compile_kwargs={"literal_binds": True})
        logger.info(f"SQL Query: {compiled_stmt}")
        results = self.db.scalars(stmt.offset(skip).limit(limit)).all()
        logger.info(f"Query Results: {results}")
        return results

    def create(self, subtask: SubTask) -> SubTask:
        self.db.add(subtask)
        self.db.commit()
        self.db.refresh(subtask)
        return subtask

    def update(self, db_subtask: SubTask, subtask_update_data: dict) -> SubTask:
        for key, value in subtask_update_data.items():
            setattr(db_subtask, key, value)
        self.db.add(db_subtask)
        self.db.commit()
        self.db.refresh(db_subtask)
        return db_subtask

    def delete(self, db_subtask: SubTask) -> None:
        self.db.delete(db_subtask)
        self.db.commit()