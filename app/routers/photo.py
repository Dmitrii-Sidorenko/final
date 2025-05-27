from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from typing import List
import os
import time
from urllib.parse import quote_plus

from starlette import status

from ..schemas import photo as photo_schema
from ..services.photo import PhotoService, get_photo_service
from ..core import deps
from ..schemas import user as user_schema

router = APIRouter(prefix="/photos", tags=["photo"])

@router.post("/", response_model=photo_schema.Photo)
async def upload_photo(
    photo: UploadFile = File(..., description="Файл для загрузки (jpeg, jpg, png, до 50 МБ)"),
    photo_service: PhotoService = Depends(get_photo_service),
    current_user: user_schema.User = Depends(deps.get_current_active_user),
):
    if photo.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неподдерживаемый формат. Допустимы: jpeg, jpg, png")
    if photo.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Размер файла превышает 50 МБ")

    files_dir = "files"
    os.makedirs(files_dir, exist_ok=True)

    filename = f"photo_{current_user.id}_{int(time.time())}_{photo.filename}"
    filepath = os.path.join(files_dir, filename)

    try:
        contents = await photo.read()
        with open(filepath, "wb") as f:
            f.write(contents)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при сохранении файла")
    finally:
        await photo.close()

    photo_data = photo_schema.PhotoCreate(filename=filename, filepath=filepath)
    return photo_service.create(photo_in=photo_data)

@router.get("/{photo_id}")
async def get_photo(
    photo_id: int,
    photo_service: PhotoService = Depends(get_photo_service),
):
    photo = photo_service.get_or_404(photo_id=photo_id)
    filepath = photo.filepath
    filename_for_download = quote_plus(photo.filename)
    content_type = ""

    if photo.filename.lower().endswith((".jpg", ".jpeg")):
        content_type = "image/jpeg"
    elif photo.filename.lower().endswith(".png"):
        content_type = "image/png"
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось определить тип содержимого")

    try:
        with open(filepath, "rb") as f:
            image_bytes = f.read()
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{filename_for_download}"
        }
        return Response(content=image_bytes, media_type=content_type, headers=headers)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фотография не найдена на сервере")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при чтении файла")