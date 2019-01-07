from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from sendgrid import SendGridAPIClient, Email
from sendgrid.helpers.mail import Mail, Content
from smtplib import SMTPException

from .cryptography import encode
from .tokens import account_activation_token

SG = SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)


class UserManager(BaseUserManager):

    def _create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        :param email: str - user's email
        :param password: str - user's password
        :param extra_fields: class User fields except of 'email', 'password'
        :return: User object
        """
        if not email:
            raise ValueError('Users must have an non-empty email address')
        if not password:
            raise ValueError('Users must have an non-empty password')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password and sets
        is_staff and is_superuser as False.
        :param email: str - user's email
        :param password: str - user's password
        :param extra_fields: class User fields except of 'email', 'password'
        :return: User object
        """
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)


def send_email_confirmation(user, to_email=None):
    """
    Sends an email on to_email
    :param user: User
    :param to_email: target email to send confirmation
    :return: Boolean
    """

    from_email = Email(settings.EMAIL_HOST_USER)
    to_email = Email(to_email if to_email else user.email)

    email_token = account_activation_token.make_token(user)

    encrypted_email = encode(to_email.email)

    subject = f'Confirm {to_email.email} on SStove'
    content = Content('text/plain', (
        f'We just needed to verify that {to_email.email} '
        f'is your email address.'
        f' Just click the link below \n'
        f'{settings.LOCAL_DOMAIN}/api/users/activate/'
        f'{encrypted_email}/{email_token}'
    ))

    mail = Mail(from_email, subject, to_email, content)

    try:
        body = mail.get()

        SG.client.mail.send.post(
            request_body=body
        )
    except SMTPException:
        return False

    return True
