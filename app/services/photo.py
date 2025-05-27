from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status, Depends

from app.core.database import get_db
from ..models import photo as photo_model
from ..schemas import photo as photo_schema
from ..repositories.photo import PhotoRepository

class PhotoService:
    """Сервис для обработки фотографий."""

    def __init__(self, photo_repo: PhotoRepository):
        """Инициализирует сервис фотографий."""
        self.photo_repo = photo_repo

    def create(self, photo_in: photo_schema.PhotoCreate) -> photo_model.Photo:
        """Создает новую фотографию."""
        db_photo = photo_model.Photo(**photo_in.model_dump())
        return self.photo_repo.create(db_photo)

    def get_or_404(self, photo_id: int, raise_exception: bool = True) -> Optional[photo_model.Photo]:
        """
        Получает фотографию по ID.
        """
        db_photo = self.photo_repo.get(photo_id)
        if db_photo is None and raise_exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фотография не найдена")
        return db_photo

    def get_all(self, skip: int = 0, limit: int = 100) -> List[photo_model.Photo]:
        """Получает список всех фотографий с возможностью пагинации."""
        return self.photo_repo.get_all(skip, limit)

    def update(self, photo_id: int, photo_update: photo_schema.PhotoUpdate) -> photo_model.Photo:
        """Обновляет информацию о существующей фотографии."""
        db_photo = self.get_or_404(photo_id)
        update_data = photo_update.model_dump(exclude_unset=True)
        return self.photo_repo.update(db_photo, update_data)

    def delete(self, photo_id: int) -> None:
        """Удаляет фотографию по ID."""
        db_photo = self.get_or_404(photo_id)
        return self.photo_repo.delete(db_photo)

def get_photo_service(db: Session = Depends(get_db)):
    """Создает и возвращает экземпляр сервиса фотографий с зависимостями."""
    photo_repo = PhotoRepository(db)
    return PhotoService(photo_repo)