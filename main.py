from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from sqlalchemy.orm import Session
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
from app.core.database import engine, get_db
from app.core.config import settings
from app.models.base import Base
from app.models.user import User
from app.schemas import UserCreate, UserWithProjects, Project  # Импортируем из __init__.py
from app.core.security import get_password_hash
from app.routers import users, auth, category, project, task, subtask, photo
from app.services.user import UserService, get_user_service

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Настройка CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(category.router, prefix=settings.API_V1_STR)
app.include_router(project.router, prefix=settings.API_V1_STR)
app.include_router(task.router, prefix=settings.API_V1_STR)
app.include_router(subtask.router, prefix=settings.API_V1_STR)
app.include_router(photo.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    await create_initial_admin()

async def create_initial_admin():
    try:
        db: Session = next(get_db())
        user_service: UserService = get_user_service(db)
        admin_email = "regressor04@gmail.com"
        admin_password = "adminpassword"

        admin = user_service.get_by_email(admin_email)
        if not admin:
            admin_data = UserCreate(email=admin_email, password=admin_password, password_confirm=admin_password, is_admin=True)
            user_service.create(admin_data)
            logging.info("Администратор создан.")
        else:
            logging.info("Администратор уже существует.")
    except Exception as e:
        logging.error(f"Ошибка при создании администратора: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.2")