from app.core.celery_app import celery_app
from app.services.email_service import EmailService

@celery_app.task(
    name= "voiceai.send_email_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
)
def send_email_task( self,user_email,subject,html):
    print("Celery task called .........................")
    email_service = EmailService()
    email_service.send_email(
        to_email=user_email,
        subject=subject,
        html_content=html,
    )
