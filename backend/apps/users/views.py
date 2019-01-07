from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView

from exceptions import ValidationError
from utils import is_user_owner

from .serializers import (RegistrationSerializer, LoginSerializer,
                          UserUpdateSerializer)
from .tokens import account_activation_token
from .backends import UserAuthentication
from .cryptography import decode
from .models import User
from .utils import send_email_confirmation


class UserLogin(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        """
        :param request: HttpRequest
        :return: Response({user_token, user_id}, status)
                 Response({message}, status)
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(
                {'message': 'Your email or password is not valid.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        user = User.objects.get(email=serializer.validated_data['email'])
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

        serializer = RegistrationSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class UserActivation(APIView):

    permission_classes = (AllowAny,)

    def post(self, request, encrypted_email, email_token):
        """
        Activates user account if the given credentials suffice
        :param request: HttpRequest
        :param encrypted_email: String
        :param email_token: String
        :return: Response({message}, status)
        """

        email = decode(encrypted_email)
        user = get_object_or_404(User, email=email)

        if user.is_active:
            return Response(
                {'message': 'User is already exists and activated'},
                status=status.HTTP_403_FORBIDDEN
            )

        if account_activation_token.check_token(user, email_token):
            user.is_active = True
            user.save()

            return Response({'message': "User's account has been activated"},
                            status=status.HTTP_201_CREATED)

        return Response({'message': 'Invalid token'},
                        status=status.HTTP_403_FORBIDDEN)


class UserRetryActivation(APIView):

    def get(self, request):
        """
        Checks non-confirmed user credentials and if so then
        sends new confirmation to its email
        :param request: HTTP Response
        :return: Response({status, message})
        """

        email = request.data.get('email')
        if not email:
            raise ValidationError('Email is required')

        user = get_object_or_404(User, email=email)

        if user.is_active:
            return Response(
                {'message': 'User already activated'},
                status=status.HTTP_403_FORBIDDEN,
            )

        send_email_confirmation(user)

        return Response(
            {'message': 'Confirmation email has been sent'},
            status=status.HTTP_202_ACCEPTED,
        )


class UserProfile(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        """
        Return user's data.
        :param request: HTTP request
        :param id: String
        :return: Response(data, status)
        """
        user = UserAuthentication.get_user(id)

        serializer = UserUpdateSerializer(user)
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

        serializer = UserUpdateSerializer(
            user,
            data=request_data,
            partial=True
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
        if not send_email_confirmation(user, valid_mail):
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
        serializer = UserUpdateSerializer(user, data=request.data,
                                          partial=True)
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
