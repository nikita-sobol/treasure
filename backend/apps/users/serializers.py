import re

from django.contrib.auth import authenticate
from rest_framework import exceptions, serializers

from exceptions import ValidationError, NotFound, PermissionDenied

from .models import User
from .utils import send_email_confirmation


class BaseLoginSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return data


class LoginSerializer(BaseLoginSerializer):

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            account_exists_error = exceptions.NotFound(
                f"Account with email and password does not exist"
            )

            raise account_exists_error

        if not user.is_active:
            activation_error = PermissionDenied(
                f'Account {user.email} has not been activated yet'
            )

            raise activation_error

        return data

    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {
            'email': {
                'validators': [],
            },
        }


class RegistrationSerializer(BaseLoginSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, is_active=False)

        send_email_confirmation(user)

        return user

    def validate_password(self, value):
        password_match = re.match(
            (r'^(?=.*[A-Za-z])(?=.*\d)' +
             r'(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,12}$'), value
        )

        if not password_match:
            raise ValidationError('Password validation failed')

        return value

    class Meta:
        model = User
        fields = ('email', 'password', 'fname')


class UserUpdateSerializer(RegistrationSerializer):

    def validate_password(self, value):

        super(UserUpdateSerializer, self).validate_password(value)

        if self.password == value:
            raise ValidationError(
                'User cannot change password on the same one'
            )

        return value

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('email', 'password', 'fname', 'lname', 'gender', 'birthdate')
        extra_kwargs = {
            'email': {'required': False},
            'password': {'required': False},
            'fname': {'required': False},
            'lname': {'required': False},
            'gender': {'required': False},
            'birthdate': {'required': False},
        }