from kimera.dxs.BaseDXS import BaseDXS
from kimera.process.TaskManager import TaskManager


class NotifyDXS(BaseDXS):
    def __init__(self, method_config: dict):
        super().__init__(method_config)
        self.task_manager = TaskManager()

    async def send_notification(self, user_id: int):
        """
        Trigger async notification task for a user.
        
        Args:
            user_id: The ID of the user to send notification to
        
        Returns:
            dict with task status and task ID
        """
        try:
            task = await self.task_manager.send_async(
                friend="notifications",
                task_name="send_user_notification",
                args=[user_id]
            )
            
            return {
                "status": "success",
                "message": f"Notification task queued for user {user_id}",
                "user_id": user_id,
                "task_id": str(task) if task else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "user_id": user_id
            }
