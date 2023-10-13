from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
import logging
import threading
import os

logger = logging.getLogger('tempname')
environment = os.environ.get('ENVIRONMENT')

mailing_active = os.environ.get('MAILING_ACTIVE', False) == 'True'


class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, sender):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        self.sender = sender
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.subject, self.html_content, self.sender, self.recipient_list)
        msg.content_subtype = 'html'
        msg.send()


class SystemMail(object):
    @staticmethod
    def make_connection():
        try:
            conn = EmailBackend(
                host=os.environ.get("EMAIL_HOST"),
                port=os.environ.get("EMAIL_PORT"),
                username=os.environ.get("EMAIL_USERNAME"),
                password=os.environ.get("EMAIL_PASSWORD"),
                use_tls=os.environ.get("EMAIL_TLS"),
                fail_silently=False
            )
            return conn
        except Exception as e:
            logger.exception(f"ERROR on connection to email: {e}")

    @classmethod
    def send_global_email(cls, email, user, conn):
        try:
            email.send()
            conn.close()
            logger.info(f"Sent email to user: {user}")
        except Exception as e:
            conn.close()

    @classmethod
    def send_email(cls, subject, content, to, message_type=None):
        # to reduce number of unimportant mail:
        if not mailing_active:
            logging.info(f"MAILING SKIPPED: {subject} | {content}")
            return

        end_message = f"<i>Ova poruka je generirana automatski.</i>"
        signature = f"<br>" \
                    f"<strong>The Falcon Technology</strong><br>" \
                    f"Vladimira Nazora 8<br>10370 Dugo Selo, Croatia"

        conn = cls.make_connection()
        email = EmailMessage(
            subject=f"tempname {environment} {subject}",
            body=f"<p>{content}</p>" \
                 f"<br>" \
                 f"<p>{end_message}</p>" \
                 f"<p>{signature}</p>",
            from_email=os.environ.get("EMAIL_FROM"),        # does not work on google smtp service!
            to=[to] if hasattr(to, '__len__') and isinstance(to, str) else to,
            connection=conn
        )
        email.content_subtype = message_type if message_type else 'html'
        t1 = threading.Thread(target=cls.send_global_email, args=(email, to, conn))
        t1.start()
        return

    """
    Generic error mail to tempname app mail
    """
    @classmethod
    def generic_system_error_mail(cls, err_msg, subject=f"SYSTEM Pogreška u sustavu"):
        content = f"Error:<br>" \
                  f"{err_msg}"
        to = os.environ.get("EMAIL_CONTACT")
        message_type = 'html'

        cls.send_email(subject, content, to, message_type)
        logger.info(f"Sent system error mail: {subject}")
        return

    @classmethod
    def generic_system_report_mail(cls, message, subject=f"SYSTEM REPORT"):
        content = f"{message}"
        to = os.environ.get("EMAIL_CONTACT")
        message_type = 'html'

        cls.send_email(subject, content, to, message_type)
        logger.info(f"Sent system report mail: {subject}")
        return

    """
    Generic mail to user
    Uses:
    - activation_email - not implemented, work in progress
    - reset_password
    """
    @classmethod
    def generic_user_mail(cls, subject, message, user):
        subject = f"{subject}"
        content = f"{message}"
        to = user
        message_type = 'html'

        cls.send_email(subject, content, to, message_type)
        return

    @classmethod
    def activation_email(cls, user=None):
        url_path = os.environ.get('FRONTEND_URL_ACTIVATION') + f'{str(user.user_detail.email_verified_code)}/{str(user.user_detail.token_code)}'
        subject = 'Aktivacija računa'
        msg = f'<p>Pozvani ste u tempname aplikaciju <b>{user.first_name} {user.last_name}</b>.<p>' \
              f'<br>' \
              f'<p>Za korištenje aplikacije trebate aktivirati vaš račun.</p>' \
              f'<p>Molimo vas da potvrdite vašu email adresu:</p>' \
              f'<p><a href="{url_path}" target="_blank">Kliknite ovdje!</a></p>'

        cls.generic_user_mail(subject, msg, user.email)
        return

    @classmethod
    def reset_password(cls, user=None):
        url_path = os.environ.get('FRONTEND_URL_RESET_PASSWORD') + f'/{str(user.user_detail.token_code)}'
        subject = 'Resetiranje lozinke'
        msg = f'<p>Pozdrav <b>{user.first_name} {user.last_name}</b>.<p>' \
              f'<br>' \
              f'<p>Zatražili ste resetiranje lozinke.</p>' \
              f'<p>Molimo slijedite upute na linku:</p>' \
              f'<p><a href="{url_path}" target="_blank">Kliknite ovdje!</a></p>'

        cls.generic_user_mail(subject, msg, user.email)
        return
