from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import exceptions, serializers
from utils import (UploadedImageField, delete_std_images_from_media)
from .models import User


class UserSerializer(serializers.ModelSerializer):

    profile_image = UploadedImageField(max_length=None)

    def update(self, instance, validated_data):
        new_image = validated_data.get('profile_image')
        old_image = instance.profile_image

        if new_image and old_image:
            delete_std_images_from_media(
                old_image,
                User.VARIATIONS_PROFILE_IMAGE
            )

        for attr, value in validated_data.items():
            if value or attr != 'profile_image':
                setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = User
        exclude = ('email', 'password')


class LoginSerializer(serializers.Serializer):

    user_email = serializers.EmailField(required=True)
    user_password = serializers.CharField(required=True)

    def validate(self, attrs):
        user_email = attrs.get('user_email', '')
        user_password = attrs.get('user_password', '')

        try:
            validate_email(user_email)
        except ValidationError:
            email_validation_error = exceptions.ValidationError
            email_validation_error.default_detail = (
                'Invalid user email format.'
            )

            raise email_validation_error

        if not user_email or not user_password:
            authorization_error = exceptions.ValidationError
            authorization_error.default_detail = (
                'User must provide email and password'
            )

            raise authorization_error

        user = authenticate(user_email=user_email,
                            user_password=user_password)
        if not user:
            account_exists_error = exceptions.ValidationError
            account_exists_error.default_detail = (
                'Account with such credentials does not exist'
            )

            raise account_exists_error

        if not user.is_active:
            activation_error = exceptions.ValidationError
            activation_error.default_detail = (
                'Account has not been activated yet'
            )

            raise activation_error

        attrs['user'] = user
        return attrs


class PasswordSerializer(serializers.ModelSerializer):

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password')

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('new_password'))
        instance.save()
        return instance


class EmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',)

    def validate(self, attrs):
        new_email = attrs.get('email')

        try:
            validate_email(new_email)
        except ValidationError:
            email_validation_error = exceptions.ValidationError
            email_validation_error.default_detail = (
                'Invalid user email format.'
            )

            raise email_validation_error

        return attrs

    def update(self, instance, validated_data):
        new_email = validated_data.get('email')
        instance.is_active = False
        instance.email = new_email
        instance.save()

        return instance
