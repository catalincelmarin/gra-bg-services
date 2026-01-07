from typing import Optional, List
from kimera.db.AutoWireRepo import AutoWireRepo


class UserRepo(AutoWireRepo):
    """
    Repository for User table using SQLAlchemy AutoWireRepo.
    Automatically maps to the 'users' table in PostgreSQL.
    """
    
    def __init__(self):
        self.model_name = "users"
        self.store_name = "postgres"
        super().__init__()
    
    async def get_by_email(self, email: str) -> Optional[any]:
        """Get user by email address"""
        users = await self.find(email=email)
        return users[0] if users else None
    
    async def get_active_users(self) -> List[any]:
        """Get all active users"""
        return await self.find(is_active=True)
    
    async def get_verified_users(self) -> List[any]:
        """Get all verified users"""
        return await self.find(is_verified=True)
