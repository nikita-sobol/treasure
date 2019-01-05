import os
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from stdimage.models import StdImageFieldFile

PROTOCOL = 'http'


def is_user_owner(request, id):
    token_user = get_token_user(request)
    user_id = settings.HASH_IDS.decode(id)[0]
    return user_id == token_user.id


def get_token_user(request):
    """
    Get user's id from token
    :param request: HTTP request
    :return: integer user_id
    """

    token_key = request.META.get('HTTP_AUTHORIZATION').split()[1]
    token = Token.objects.get(key=token_key)
    return token.user


def get_changed_uri(request, param_name, val):
    """
    Changes value of url parameter in url from request.

    :param request: rest_framework.request.Request object
    :param param_name: string with name of parameter in url to be changed
    :param val: new value to be set to parameter
    :return: url from request with changed parameter value
    """
    params = request.GET.copy()
    params[param_name] = val
    request_uri = request.build_absolute_uri()
    return request_uri.split('?')[0] + '?' + params.urlencode()