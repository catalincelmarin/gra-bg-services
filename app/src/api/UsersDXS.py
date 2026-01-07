from kimera.dxs.BaseDXS import BaseDXS
from app.src.data.repos.UserRepo import UserRepo


class UsersDXS(BaseDXS):
    def __init__(self, method_config: dict):
        super().__init__(method_config)
        self.user_repo = UserRepo()

    async def list_users(self):
        """Get all users from PostgreSQL database"""
        try:
            await self.user_repo.connect()
            users = await self.user_repo.all()
            
            users_list = []
            for user in users:
                user_dict = {}
                for column in user.__table__.columns:
                    value = getattr(user, column.name)
                    if hasattr(value, 'isoformat'):
                        user_dict[column.name] = value.isoformat()
                    else:
                        user_dict[column.name] = value
                
                if 'password' in user_dict:
                    del user_dict['password']
                
                users_list.append(user_dict)
            
            return {
                "status": "success",
                "count": len(users_list),
                "users": users_list
            }
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
