from re import match
from django.contrib.auth import authenticate
from rest_framework import exceptions, serializers

from exceptions import ValidationError, NotFound, PermissionDenied

from .models import User


class BaseSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        return {key: value[0] for key, value in dict(data).items()}


class LoginSerializer(BaseSerializer):

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            account_exists_error = exceptions.NotFound(
                f'Account with email: {user.email} '
                f'and password: {user["password"]} does not exist'
            )

            raise account_exists_error

        if not user.is_active:
            activation_error = PermissionDenied(
                f'Account {user.email}has not been activated yet'
            )

            raise activation_error

        return data

    class Meta:
        model = User
        fields = ('email', 'password')


class RegistrationSerializer(BaseSerializer):

    def create(self, validated_data):
        # TODO: PUT SENDING EMAIL HERE

        user = User.objects.create_user(**validated_data, is_active=False)
        return user

    def validate_email(self, value):
        if value and User.objects.get(email=value):
            raise ValidationError('User with such email already exists')

        return value

    def validate_password(self, value):
        if not match(f'^(?=.*[A-Za-z])(?=.*\d)'
                     f'(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8, 12}$'):
            raise ValidationError('Password validation failed')

        return value

    class Meta:
        model = User
        fields = ('email', 'password', 'fname')


class UserUpdateSerializer(RegistrationSerializer):

    def validate_password(self, value):

        if self.password == value:
            raise ValidationError(
                'User cannot change password on the same one'
            )

        if value and not match(f'^(?=.*[A-Za-z])(?=.*\d)'
                               f'(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8, 12}$'):
            raise ValidationError('Password validation failed')

        return value

    def validate_email(self, value):
        if value and User.objects.get(email=value):
            raise ValidationError('User with such email already exists')

        return value

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('email', 'password', 'fname', 'gender')
