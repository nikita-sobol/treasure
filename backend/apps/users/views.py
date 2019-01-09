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

from .serializers import (RegistrationSerializer, LoginSerializer)
from .tokens import account_activation_token
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
