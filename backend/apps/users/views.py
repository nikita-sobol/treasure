from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import (ValidationError, validate_email)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView
from sendgrid import SendGridAPIClient, Email
from sendgrid.helpers.mail import Mail, Content
from smtplib import SMTPException

from utils import is_user_owner

from .serializers import (EmailSerializer, LoginSerializer, PasswordSerializer,
                          UserSerializer)
from .tokens import account_activation_token
from .backends import UserAuthentication
from .cryptography import decode, encode
from .models import User


class UserLogin(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        """
        :param request: HttpRequest
        :return: Response({user_token, user_id}, status)
                 Response({message}, status)
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'message': 'Your email or password is not valid.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.validated_data['user']
        user_token, _ = Token.objects.get_or_create(user=user)

        if not TokenValidation.is_token_active(user_token):
            user_token.delete()
            user_token = Token.objects.create(user=user)

        return Response({
            'token': user_token.key,
        }, status=status.HTTP_200_OK)


class UserLogout(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Deletes user's token after logout
        :param request: HttpRequest
        :return: Response({message}, status)
        """
        token_key = request.META['HTTP_AUTHORIZATION'][6:]
        Token.objects.get(key=token_key).delete()

        return Response({'message': 'User has been logged out'},
                        status=status.HTTP_200_OK)


class UserRegistration(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        """
        If user credentials are valid then creates deactivated User
        :param request: http request
        :return: Response({status, message})
        """
        user_email = request.data.get('user_email')
        user_password = request.data.get('user_password')
        user_first_name = request.data.get('first_name')

        if not (user_email and user_password and user_first_name):
            return Response({'message': 'Some credentials were not provided'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(user_email)
        except ValidationError as error:
            return Response({'message': 'Invalid email format'},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=user_email).exists():
            return Response({'message': 'User with such email already exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(email=user_email,
                                        password=user_password,
                                        first_name=user_first_name,
                                        is_active=False)

        if not UserActivation.send_email_confirmation(user):
            return Response({
                'message': 'The mail has not been delivered'
                           ' due to connection reasons'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_201_CREATED)


class UserActivation(APIView):

    permission_classes = (AllowAny,)

    sg = SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

    def post(self, request, encrypted_email, email_token):
        """
        Activates user account if the given credentials suffice
        :param request: HttpRequest
        :param encrypted_email: String
        :param email_token: String
        :return: Response({message}, status)
        """

        user_email = decode(encrypted_email)
        user = get_object_or_404(User, email=user_email)

        if user.is_active:
            return Response({'message': 'User is already exists and activated'},
                            status=status.HTTP_403_FORBIDDEN)

        if account_activation_token.check_token(user, email_token):
            user.is_active = True
            user.save()

            return Response({'message': "User's account has been activated"},
                            status=status.HTTP_201_CREATED)

        return Response({'message': 'Invalid token'},
                        status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def send_email_confirmation(user, to_email=None):
        """
        Sends an email on specified user.email
        :param user: User
        :param to_email: target email to send confirmation
        :return: Boolean
        """

        if to_email is None:
            to_email = Email(user.email)
        from_email = Email(settings.EMAIL_HOST_USER)

        email_token = account_activation_token.make_token(user)

        encrypted_email = encode(to_email.email)

        subject = f'Confirm {to_email.email} on SStove'
        content = Content('text/plain', (
            f'We just needed to verify that {to_email.email} '
            f'is your email address.'
            f' Just click the link below \n'
            f'{settings.LOCAL_DOMAIN}/api/users/activate/'
            f'{encrypted_email}/{email_token}/'
        ))

        mail = Mail(from_email, subject, to_email, content)

        try:
            body = mail.get()

            UserActivation.sg.client.mail.send.post(
                request_body=body
            )
        except SMTPException:
            return False

        return True


class UserRetryActivation(APIView):

    def get(self, request):
        """
        Checks non-confirmed user credentials and if so then
        sends new confirmation to its email
        :param request: HTTP Response
        :return: Response({status, message})
        """

        user_email = request.data.get('user_email')

        try:
            validate_email(user_email)
        except ValidationError:
            return Response(
                {'message': 'Email validation failed'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        user = get_object_or_404(User, email=user_email)

        if user.is_active:
            return Response(
                {'message': 'User already activated'},
                status=status.HTTP_403_FORBIDDEN,
            )

        is_activation_mail_sent = UserActivation.send_email_confirmation(user)

        if not is_activation_mail_sent:
            return Response({
                'message': 'The mail has not been delivered'
                           ' due to connection reasons'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {'message': 'Confirmation email has been sent'},
            status=status.HTTP_202_ACCEPTED,
        )


class UserProfile(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    variation = User.medium

    def get(self, request, id):
        """
        Return user's data.
        :param request: HTTP request
        :param id: String
        :return: Response(data, status)
        """
        user = UserAuthentication.get_user(id)
        context = {
            'variation': self.variation,
            'domain': get_current_site(request)
        }

        serializer = UserSerializer(user, context=context)
        response_data = serializer.data

        enable_editing_profile = is_user_owner(request, id)
        response_data['enable_editing_profile'] = enable_editing_profile

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, id):
        """
        Update user's data
        :param request: HTTP request
        :param id: String
        :return: Response(data, status)
        """
        if not is_user_owner(request, id):
            return Response({'message': 'Editing not allowed'},
                            status=status.HTTP_403_FORBIDDEN)

        user = UserAuthentication.get_user(id)
        request_data = request.data.copy()
        context = {
            'variation': self.variation,
            'domain': get_current_site(request)
        }
        serializer = UserSerializer(
            user,
            data=request_data,
            partial=True,
            context=context,
        )
        if serializer.is_valid():
            serializer.save(id=user.id, **serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class UserEmail(APIView):

    def patch(self, request, id):
        """
        Changes user email
        :param request: HTTP Request
        :param id: String
        :return: Response(data)
        """
        new_email = request.data.get('email')
        if not new_email:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = UserAuthentication.get_user(id)
        if User.objects.filter(email=new_email).exists():
            return Response({'message': 'User with such email already exists'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = EmailSerializer(user, request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        valid_mail = serializer.validated_data['email']
        if not UserActivation.send_email_confirmation(user, valid_mail):
            return Response({
                'message': 'The mail has not been delivered'
                           ' due to connection reasons'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer.update(user, serializer.validated_data)
        return Response(status=status.HTTP_200_OK)


class UserPassword(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, id):
        """
        :param request: HTTP request
        :param id: String
        :return: Response(message, status)
        """
        user = UserAuthentication.get_user(id)
        serializer = PasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(serializer.data.get('old_password')):
            return Response({'message': 'Wrong password'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.update(user, serializer.data)

        return Response({
            'message': 'Password was updated. '
                       'Please re-login to renew your session'
        }, status=status.HTTP_200_OK)


class TokenValidation(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        :param request: HTTP request
        :return: Response(status)
        """
        token_key = request.META.get('HTTP_AUTHORIZATION')[6:]
        token = Token.objects.get(key=token_key)
        if TokenValidation.is_token_active(token):
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def is_token_active(token):
        if (timezone.now() > token.created + settings.USER_TOKEN_LIFETIME or
                token is None):
            return False

        return True
