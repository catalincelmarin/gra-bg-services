from typing import Dict, Any, Optional
from kimera.process.TaskManager import TaskManager


class NotificationHandlers:
    """
    Static handler methods for notification actions.
    Each handler method follows the naming convention: {action}_handler
    
    All handlers receive:
    - body: Dict[str, Any] (mandatory) - The message payload
    - metadata: Optional[Dict[str, Any]] (optional) - Additional context
    """
    
    @staticmethod
    async def email_handler(body: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Handle email notification requests.
        
        Expected body structure:
        {
            "user_id": int,
            "template": str,  # e.g., "password_reset", "password_recovery"
            "data": dict  # Template-specific data
        }
        
        Args:
            body: Message body containing user_id and email details
            metadata: Optional metadata for tracking/debugging
        """
        try:
            user_id = body.get("user_id")
            template = body.get("template")
            template_data = body.get("data", {})
            
            if not user_id:
                print(f"[EMAIL_HANDLER] Error: user_id is required in body")
                return
            
            if not template:
                print(f"[EMAIL_HANDLER] Error: template is required in body")
                return
            
            print(f"[EMAIL_HANDLER] Processing email for user_id={user_id}, template={template}")
            print(f"[EMAIL_HANDLER] Template data: {template_data}")
            
            # Get TaskManager singleton
            task_manager = TaskManager()
            
            # Queue the email task asynchronously via Celery
            await task_manager.send_async(
                task_name="send_email",
                friend="notifications",
                args=[user_id, template, template_data],
                kwargs={"metadata": metadata}
            )
            
            print(f"[EMAIL_HANDLER] Email task queued successfully for user_id={user_id}")
            
        except Exception as e:
            print(f"[EMAIL_HANDLER] Error: {e}")
            if metadata:
                print(f"[EMAIL_HANDLER] Metadata: {metadata}")
    
    @staticmethod
    async def whatsapp_handler(body: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Handle WhatsApp notification requests.
        
        Expected body structure:
        {
            "user_id": int,
            "template": str,
            "data": dict
        }
        
        Args:
            body: Message body containing user_id and WhatsApp details
            metadata: Optional metadata for tracking/debugging
        """
        try:
            user_id = body.get("user_id")
            template = body.get("template")
            template_data = body.get("data", {})
            
            if not user_id:
                print(f"[WHATSAPP_HANDLER] Error: user_id is required in body")
                return
            
            if not template:
                print(f"[WHATSAPP_HANDLER] Error: template is required in body")
                return
            
            print(f"[WHATSAPP_HANDLER] Processing WhatsApp message for user_id={user_id}, template={template}")
            
            # Get TaskManager singleton
            task_manager = TaskManager()
            
            # Queue the WhatsApp task asynchronously via Celery
            await task_manager.send_async(
                task_name="send_whatsapp",
                friend="notifications",
                args=[user_id, template, template_data],
                kwargs={"metadata": metadata}
            )
            
            print(f"[WHATSAPP_HANDLER] WhatsApp task queued successfully for user_id={user_id}")
            
        except Exception as e:
            print(f"[WHATSAPP_HANDLER] Error: {e}")
            if metadata:
                print(f"[WHATSAPP_HANDLER] Metadata: {metadata}")
