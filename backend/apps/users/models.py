from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from rest_framework import exceptions

from .utils import UserManager


class User(AbstractBaseUser, PermissionsMixin):

    male, female, other, unknown = 'F', 'M', 'O', 'U'
    GENDER_CHOICES = (
        (female, 'female'),
        (male, 'male'),
        (other, 'other'),
        (unknown, 'unknown'),
    )

    email = models.EmailField(max_length=255, unique=True)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=2,
                              default=unknown)

    is_active = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    @staticmethod
    def get_user(user_id):
        """
        Returns user by id
        :param user_id: int
        :return: User
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.NotFound(detail='User does not exist')
