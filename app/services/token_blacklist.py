# services/token_blacklist.py
from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.database import get_db
from ..repositories.token_blacklist import TokenBlacklistRepository
from ..models.token_blacklist import TokenBlacklist

class TokenBlacklistService:
    def __init__(self, token_blacklist_repo: TokenBlacklistRepository):
        self.token_blacklist_repo = token_blacklist_repo

    def add(self, token: str) -> TokenBlacklist:
        return self.token_blacklist_repo.add(token)

    def is_blacklisted(self, token: str) -> bool:
        return self.token_blacklist_repo.check(token) is not None

def get_token_blacklist_service(db: Session = Depends(get_db)):
    token_blacklist_repo = TokenBlacklistRepository(db)
    return TokenBlacklistService(token_blacklist_repo)