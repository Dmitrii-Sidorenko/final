from sqlalchemy.orm import Session
from typing import Optional, List

from ..models.photo import Photo

class PhotoRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, photo: Photo) -> Photo:
        self.db.add(photo)
        self.db.commit()
        self.db.refresh(photo)
        return photo

    def get(self, photo_id: int) -> Optional[Photo]:
        return self.db.query(Photo).filter(Photo.id == photo_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Photo]:
        return self.db.query(Photo).offset(skip).limit(limit).all()

    def update(self, db_photo: Photo, photo_update_data: dict) -> Photo:
        for key, value in photo_update_data.items():
            setattr(db_photo, key, value)
        self.db.add(db_photo)
        self.db.commit()
        self.db.refresh(db_photo)
        return db_photo

    def delete(self, db_photo: Photo) -> None:
        self.db.delete(db_photo)
        self.db.commit()