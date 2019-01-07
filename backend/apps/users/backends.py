from rest_framework import exceptions

from .models import User


class UserAuthentication:

    def authenticate(self, request, email=None,
                     password=None, user_token=None):
        """
        User credentials are being processed on the valid format.
        If User credentials are valid then will be returned User instance.
        If No then None.
        :param request: HttpRequest
        :param user_email: String
        :param user_password: String
        :param user_token: String
        :return: User object or None
        """

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

        return None

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
