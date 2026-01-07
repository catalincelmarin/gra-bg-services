import asyncio
import os
from celery import Celery
from kimera.Bootstrap import Bootstrap
from app.src.data.repos.UserRepo import UserRepo
from app.src.data.repos.CommTemplateRepo import CommTemplateRepo
from app.ext.mail.src.mailers.resend.Resend import Resend


boot = Bootstrap()
celery_app = Celery(
    broker=boot.celery_broker,
    backend=boot.celery_backend
)


@celery_app.task(name='app.src.background.notifications.send_user_notification')
def send_user_notification(user_id: int):
    """
    Background task to get user email by ID and print it.
    
    Args:
        user_id: The ID of the user to fetch
    
    Returns:
        dict with status and user email
    """
    try:
        async def get_user_email():
            user_repo = UserRepo()
            await user_repo.connect()
            
            user = await user_repo.get(user_id)
            
            if user:
                user_email = user.email
                print(f"=" * 80)
                print(f"NOTIFICATION TASK - User ID: {user_id}")
                print(f"User Email: {user_email}")
                print(f"=" * 80)
                
                return {
                    "status": "success",
                    "user_id": user_id,
                    "email": user_email
                }
            else:
                print(f"User with ID {user_id} not found")
                return {
                    "status": "error",
                    "message": f"User with ID {user_id} not found"
                }
        
        result = asyncio.run(get_user_email())
        return result
        
    except Exception as e:
        print(f"Error in send_user_notification: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@celery_app.task(name='app.src.background.notifications.send_email')
def send_email(user_id: str, template: str, template_data: dict, metadata: dict = None):
    """
    Background task to send email notifications.
    
    Args:
        user_id: The ID of the user
        template: Email template key_name (e.g., 'password_reset')
        template_data: Data for the email template (must include 'language' key)
        metadata: Optional metadata for tracking
    
    Returns:
        dict with status
    """
    try:
        print(f"=" * 80)
        print(f"[SEND_EMAIL] Processing email task")
        print(f"User ID: {user_id}")
        print(f"Template: {template}")
        print(f"Template Data: {template_data}")
        if metadata:
            print(f"Metadata: {metadata}")
        print(f"=" * 80)
        
        async def process_email():
            # Get language from template_data, default to 'en'
            language = template_data.get('language', 'en')
            
            # Initialize template repository
            template_repo = CommTemplateRepo()
            await template_repo.connect()
            
            # Fetch template with localization
            email_template = await template_repo.get_template_by_key_and_language(
                key_name=template,
                language=language
            )
            
            if not email_template:
                print(f"[SEND_EMAIL] Template '{template}' not found for language '{language}'")
                return {
                    "status": "error",
                    "message": f"Template '{template}' not found"
                }
            
            print(f"[SEND_EMAIL] Template retrieved:")
            print(f"  - Template ID: {email_template['id']}")
            print(f"  - Template Type: {email_template['template_type']}")
            print(f"  - Key Name: {email_template['key_name']}")
            print(f"  - Language: {email_template['localization']['locale_short_name']}")
            print(f"  - Subject (raw): {email_template['localization']['subject']}")
            print(f"  - Content Preview (raw): {email_template['localization']['content'][:100]}...")
            
            # Render template by replacing {{variables}} with data
            rendered_subject = template_repo.render_template(
                email_template['localization']['subject'],
                template_data
            )
            rendered_content = template_repo.render_template(
                email_template['localization']['content'],
                template_data
            )
            
            print(f"[SEND_EMAIL] Rendered template:")
            print(f"  - Subject: {rendered_subject}")
            print(f"  - Content (full):")
            print("=" * 80)
            print(rendered_content)
            print("=" * 80)
            
            # Send email via Resend mailer
            recipient_email = template_data.get('email')
            if not recipient_email:
                print("[SEND_EMAIL] ERROR: No recipient email in template_data")
                return {
                    "status": "error",
                    "message": "No recipient email provided"
                }
            
            try:
                print(f"[SEND_EMAIL] Sending email to {recipient_email}...")
                
                mailer = Resend()
                success = mailer.mailer_send(
                    mailer="default",
                    to=recipient_email,
                    subject=rendered_subject,
                    body=rendered_content
                )
                
                if success:
                    print(f"[SEND_EMAIL] Email sent successfully!")
                    
                    return {
                        "status": "success",
                        "user_id": user_id,
                        "template": template,
                        "language": language,
                        "template_id": email_template['id'],
                        "subject": rendered_subject,
                        "recipient": recipient_email,
                        "message": "Email sent successfully via Resend"
                    }
                else:
                    print(f"[SEND_EMAIL] Failed to send email")
                    return {
                        "status": "error",
                        "message": "Failed to send email via Resend"
                    }
                
            except Exception as email_error:
                print(f"[SEND_EMAIL] Failed to send email: {email_error}")
                return {
                    "status": "error",
                    "message": f"Failed to send email: {str(email_error)}"
                }
        
        result = asyncio.run(process_email())
        return result
        
    except Exception as e:
        print(f"Error in send_email: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }
