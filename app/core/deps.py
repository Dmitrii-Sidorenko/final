from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session
import logging

from app.core.config import settings
from app.core.database import get_db
from ..services.user import UserService, get_user_service
from ..schemas import user as user_schema
from ..services.reset_password import ResetPasswordService, get_reset_password_service
from ..services.token_blacklist import TokenBlacklistService, get_token_blacklist_service
from ..models.user import User
from ..models.reset_password_token import ResetPasswordToken

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_scheme = reusable_oauth2

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2),
    user_service: UserService = Depends(get_user_service),
    token_blacklist_service: TokenBlacklistService = Depends(get_token_blacklist_service),
) -> User:
    logger.info("Начало получения текущего пользователя.")
    try:
        payload: dict = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            logger.warning("Не удалось извлечь user_id из токена.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не удалось подтвердить учетные данные")
        user: User = user_service.get(user_id)
        if not user:
            logger.warning(f"Пользователь с ID {user_id} не найден.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

        # Проверка черного списка
        if token_blacklist_service.is_blacklisted(token):
            logger.warning(f"Токен {token} находится в черном списке.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен недействителен или был отозван")

        logger.info(f"Пользователь с ID {user_id} успешно получен.")
        return user
    except jwt.JWTError:
        logger.warning("Ошибка декодирования JWT.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не удалось подтвердить учетные данные")
    except HTTPException as e:
        logger.error(f"HTTPException при получении пользователя: {e}")
        raise e
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при получении пользователя: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера")

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> user_schema.User:
    logger.info(f"Проверка активности пользователя {current_user.id}. Is admin: {current_user.is_admin}") # Добавлено логирование
    if not current_user.is_active:
        logger.warning(f"Пользователь {current_user.id} не активен.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неактивный пользователь")
    logger.info(f"Пользователь {current_user.id} активен.")
    return user_schema.User.from_orm(current_user)

async def get_current_active_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Получение активного администратора."""
    logger.info(f"Проверка прав администратора для пользователя {current_user.id}.")
    if not current_user.is_admin:
        logger.warning(f"Пользователь {current_user.id} не является администратором.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав администратора")
    logger.info(f"Пользователь {current_user.id} является администратором.")
    return current_user

async def get_reset_password_token(
    token: str = Query(...),
    reset_password_service: ResetPasswordService = Depends(get_reset_password_service),
) -> ResetPasswordToken:
    logger.info(f"Получение токена восстановления пароля: {token}")

    from ..repositories.reset_password_token import ResetPasswordTokenRepository
    db: Session = Depends(get_db)()
    token_repo = ResetPasswordTokenRepository(db)
    reset_token = token_repo.get(token)
    if not reset_token:
        logger.warning(f"Токен восстановления пароля не найден: {token}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Недействительный токен восстановления пароля"
        )
    return reset_token

async def check_reset_password_token_expiration(
    reset_token: ResetPasswordToken = Depends(get_reset_password_token),
    reset_password_service: ResetPasswordService = Depends(get_reset_password_service),
):
    logger.info(f"Проверка срока действия токена восстановления пароля: {reset_token.token}")
    from datetime import datetime, timezone
    if datetime.now(timezone.utc) > reset_token.expires:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Токен истек")