import random
import string
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os

from app.core.config import settings  # Import settings from config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def generate_random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!#$%&*+-.<=>?@^_"
    return ''.join(random.choice(alphabet) for i in range(length))


SECRET_KEY = settings.SECRET_KEY

cipher_suite = Fernet(SECRET_KEY.encode())

def encrypt_token(plain_text_token: str) -> str:
    encrypted_token = cipher_suite.encrypt(plain_text_token.encode())
    return encrypted_token.decode()

def decrypt_token(encrypted_token: str) -> str:
    try:
        decrypted_token = cipher_suite.decrypt(encrypted_token.encode())
        return decrypted_token.decode()
    except Exception as e:
        print(f"Error decrypting token: {e}")
        return None


def generate_random_string(length: int = 32, chars: str = string.ascii_letters + string.digits) -> str:
    return ''.join(random.choice(chars) for i in range(length))

def generate_verification_code(length: int = 6) -> str:
    return ''.join(random.choice(string.digits) for i in range(length))


    random_string = generate_random_string()
    print(f"Random string: {random_string}")

    verification_code = generate_verification_code()
    print(f"Verification code: {verification_code}")