# app/core/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, errors
from pydantic import EmailStr
import logging
import random

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_registration_email(email: EmailStr, password: str):
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS,
    )

    message = MessageSchema(
        subject="Добро пожаловать в MultiTasker!",
        recipients=[email],
        body=f"Email: {email}\nПароль: {password}",
        subtype="plain"
    )

    fm = FastMail(conf)
    logger.info(f"Попытка отправки регистрационного письма на {email}...")
    logger.debug(f"Конфигурация FastMail: {conf}")
    logger.debug(f"Сообщение для отправки: {message.dict()}")
    try:
        logger.info("Вызов fm.send_message...")
        result = await fm.send_message(message)
        logger.info(f"Результат отправки регистрационного письма на {email}: {result}")
    except errors.ConnectionErrors as e:
        logger.error(f"Ошибка подключения к SMTP-серверу при регистрации: {e}")
    except errors.MessageErrors as e:
        logger.error(f"Ошибка отправки письма при регистрации: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при отправке письма при регистрации: {e}")

async def send_reset_password_email(email: EmailStr) -> str:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS,
    )

    code = str(random.randint(10000, 99999))

    message = MessageSchema(
        subject="Восстановление пароля",
        recipients=[email],
        body=f"Ваш код восстановления пароля: {code}",
        subtype="plain"
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        logger.info(f"Код восстановления пароля отправлен на {email}: {code}")
    except errors.ConnectionErrors as e:
        logger.error(f"Ошибка подключения к SMTP-серверу: {e}")
    except errors.MessageErrors as e:
        logger.error(f"Ошибка отправки письма: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при отправке письма: {e}")

    return code