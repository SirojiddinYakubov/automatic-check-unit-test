from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string


class SendEmailServise:
    @staticmethod
    def send_email(email, otp_code):
        try:
            subject = 'Welcome to Our Service!'
            message = render_to_string('emails/email_template.html', {
                'email': email,
                'otp_code': otp_code
            })

            email = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email]
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)

            return 200
        except Exception:
            return 400
