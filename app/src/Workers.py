import os
from kimera.comm.Intercom import Intercom, Message
from src.comm_types import CommMessage
from src.notifications import NotificationHandlers


class Workers:
    """
    Static worker coroutines for background processes.
    Following Java standards for static utility classes.
    """

    @staticmethod
    async def comm_queue_worker(**kwargs):
        """
        Worker coroutine for COMM_QUEUE Redis pub/sub.
        Runs in a separate process via Spawner.
        
        Args:
            **kwargs: Additional parameters (stop_event passed by Spawner)
        """
        # Note: stop_event is managed by Spawner's _graceful_task_wrapper
        comm_queue = Intercom(os.getenv("COMM_QUEUE"))
        
        async def handle_message(data):
            """
            Handle incoming messages from COMM_QUEUE.
            All messages must conform to CommMessage standard (scope, action, body).
            """
            try:
                # Parse and validate the message
                comm_msg = CommMessage(**data)
                
                print(f"[COMM_QUEUE] Received: scope={comm_msg.scope}, action={comm_msg.action}")
                
                # Route message based on scope
                if comm_msg.scope == "notifications":
                    # Dynamic handler resolution: action + "_handler"
                    handler_name = f"{comm_msg.action}_handler"
                    
                    if hasattr(NotificationHandlers, handler_name):
                        handler = getattr(NotificationHandlers, handler_name)
                        await handler(comm_msg.body, comm_msg.metadata)
                    else:
                        print(f"[COMM_QUEUE] No handler found for action: {comm_msg.action}")
                        print(f"[COMM_QUEUE] Expected handler method: {handler_name}")
                
                # Add more scope routing here as needed
                # elif comm_msg.scope == "booking":
                #     await handle_booking(comm_msg)
                
            except Exception as e:
                print(f"[COMM_QUEUE] Error processing message: {e}")
                print(f"[COMM_QUEUE] Invalid message data: {data}")
        
        # Subscribe to the communication queue channel
        await comm_queue.subscribe("comm", handle_message)
