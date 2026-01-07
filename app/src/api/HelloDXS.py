from kimera.dxs.BaseDXS import BaseDXS
from app.ext.mail.src.mailers.resend.Resend import Resend


class HelloDXS(BaseDXS):
    def __init__(self, method_config: dict):
        super().__init__(method_config)
        self.mailer = Resend()

    async def get_hello(self):
        """Simple hello world endpoint that sends an email"""
        try:
            email_sent = self.mailer.mailer_send(
                mailer="default",
                to="catalin@orson.ro",
                subject="Hello from GRA!",
                body="<h1>Hello!</h1><p>The hello endpoint was called successfully.</p>"
            )
            
            return {
                "message": "Hello World from GRA!",
                "status": "success",
                "email_sent": email_sent
            }
        except Exception as e:
            return {
                "message": "Hello World from GRA!",
                "status": "success",
                "email_sent": False,
                "email_error": str(e)
            }
