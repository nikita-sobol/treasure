from rest_framework.authtoken.models import Token


def is_user_owner(request, id):
    token_user = get_request_user(request)
    return id == token_user.id


def get_request_user(request):
    """
    Get user's id from token
    :param request: HTTP request
    :return: integer user_id
    """

    token_key = request.META.get('HTTP_AUTHORIZATION').split()[1]
    token = Token.objects.get(key=token_key)
    return token.user
