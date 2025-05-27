from sqlalchemy.orm import Session
from typing import Optional

from ..models.token_blacklist import TokenBlacklist

class TokenBlacklistRepository:

    def __init__(self, db: Session):
        self.db = db

    def add(self, token: str) -> TokenBlacklist:
        db_token = TokenBlacklist(token=token)
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def check(self, token: str) -> Optional[TokenBlacklist]:
        return self.db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()