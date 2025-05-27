from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.sql.expression import Select
import logging

from ..models import Category, User
from ..models.project import Project
from ..schemas.project import ProjectFilter

logger = logging.getLogger(__name__)

class ProjectRepository:

    def __init__(self, db: Session):
        self.db = db

    def get(self, project_id: int) -> Optional[Project]:
        stmt = select(Project).options(joinedload(Project.participants)).where(Project.id == project_id)
        return self.db.scalar(stmt)

    def get_with_tasks(self, project_id: int) -> Optional[Project]:
        stmt = select(Project).options(
            joinedload(Project.tasks),
            joinedload(Project.participants),
            joinedload(Project.owner)
        ).where(Project.id == project_id)
        return self.db.scalar(stmt)

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, db_project: Project, project_update_data: dict) -> Project:
        for key, value in project_update_data.items():
            setattr(db_project, key, value)
        self.db.add(db_project)
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def delete(self, db_project: Project) -> None:
        self.db.delete(db_project)
        self.db.commit()

    def get_category(self, category_id: int) -> Optional[Category]:
        stmt = select(Category).where(Category.id == category_id)
        return self.db.scalar(stmt)

    def get_projects(self, filters: ProjectFilter) -> List[Project]:
        stmt = select(Project).options(joinedload(Project.participants))
        conditions = []
        filter_params = filters.model_dump(exclude_unset=True)

        filter_mapping: Dict[str, Dict[str, Any]] = {
            "category_id": {"attribute": Project.category_id, "operator": "=="},
            "owner_id": {"attribute": Project.owner_id, "operator": "=="},
            "title": {"attribute": Project.title, "operator": "ilike", "format": "%{}%"},
            "description": {"attribute": Project.description, "operator": "ilike", "format": "%{}%"},
            "created_at_start": {"attribute": Project.created_at, "operator": ">="},
            "created_at_end": {"attribute": Project.created_at, "operator": "<="},
            "icon_id": {"attribute": Project.icon_id, "operator": "=="},
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

        results = self.db.execute(stmt).scalars().unique().all()
        logger.info(f"Query Results: {results}")
        return results

    def add_user_to_project(self, project: Project, user: User) -> Project:
        project.participants.append(user)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project