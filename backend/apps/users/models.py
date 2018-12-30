""" Custom models for user """

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from stdimage import models as std_models
from apps.utils import make_media_file_path


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
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password and sets
        is_staff and is_superuser as True.
        :param email: str - user's email
        :param password: str - user's password
        :param extra_fields: class User fields except of email, password,
        is_staff, is_superuser
        :return: User object
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    man, woman, other, unknown = 'M', 'W', 'O', 'U'
    GENDER_CHOICES = (
        (woman, 'woman'),
        (man, 'man'),
        (other, 'other'),
        (unknown, 'unknown'),
    )

    large = 'large'
    thumbnail = 'thumbnail'
    medium = 'medium'

    VARIATIONS_PROFILE_IMAGE = {
        large: (600, 400, True),
        thumbnail: (100, 100, True),
        medium: (300, 200, True),
    }

    def _make_upload_profile_image(self, filename):
        """
        Function which creates path for user's image.
        Should be used as base-function for function in parameter upload_to of
        ImageField.

        :param self: instance of User
        :param filename: name of the user's file, ex. 'image.png'
        :return: path to image or None if filename is empty
        """

        return make_media_file_path(
            model_name='User',
            attr_name='profile_image',
            original_filename=filename
        )

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=2,
                              default=unknown)
    profile_image = std_models.StdImageField(
        upload_to=_make_upload_profile_image,
        blank=True,
        null=True,
        default='',
        variations=VARIATIONS_PROFILE_IMAGE,
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = f'{self.first_name} { self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user. (only first_name)
        """
        return self.first_name
