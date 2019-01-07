from django.conf import settings
from rest_framework.authtoken.models import Token

PROTOCOL = 'http'


def is_user_owner(request, id):
    token_user = get_token_user(request)
    return id == token_user.id


def get_token_user(request):
    """
    Get user's id from token
    :param request: HTTP request
    :return: integer user_id
    """

    token_key = request.META.get('HTTP_AUTHORIZATION').split()[1]
    token = Token.objects.get(key=token_key)
    return token.user
