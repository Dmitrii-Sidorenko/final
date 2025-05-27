from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import logging

from sqlalchemy.orm import Session

from ..core import deps
from app.core.database import get_db
from ..schemas import user as user_schema
from ..schemas import reset_password as reset_password_schema
from app.core.config import settings
from app.core.deps import get_current_active_user, oauth2_scheme
from ..services.auth import AuthService, get_auth_service
from ..services.token_blacklist import TokenBlacklistService, get_token_blacklist_service
from ..services.reset_password import ResetPasswordService, get_reset_password_service

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: user_schema.UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return auth_service.register_user(user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=user_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: user_schema.User = Depends(deps.get_current_active_user),
    token: str = Depends(oauth2_scheme),
    token_blacklist_service: TokenBlacklistService = Depends(get_token_blacklist_service),
):
    logger.info(f"Пользователь {current_user.email} выполнил выход. Токен добавлен в черный список.")
    token_blacklist_service.add(token)
    return


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    reset_password_request: reset_password_schema.ResetPasswordRequest,
    reset_password_service: ResetPasswordService = Depends(get_reset_password_service)
):
    try:
        return await reset_password_service.request_reset_password(reset_password_request, db=Depends(get_db))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_password_data: reset_password_schema.ResetPassword,
    reset_password_service: ResetPasswordService = Depends(get_reset_password_service),
    db: Session = Depends(get_db)
):
    logger.info(f"Получен токен от пользователя: '{reset_password_data.token}'")
    try:
        result = await reset_password_service.confirm_reset_password(reset_password_data, db=db)
        return result
    except HTTPException as e:
        logger.warning(f"HTTPException в /reset-password: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Неожиданная ошибка в /reset-password: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))