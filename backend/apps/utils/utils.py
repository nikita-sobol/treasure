import os
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from stdimage.models import StdImageFieldFile

PROTOCOL = 'http'


def make_media_file_path(model_name, attr_name, original_filename):
    """
    Function which creates path for user's file in media folder using uuid.

    :param model_name: class of instance
    :param attr_name: attribute for which image is saved
    :param original_filename: original filename of the image, ex. 'image.jpg'
    :return: path from MEDIA_ROOT to file or None if filename is empty
    """
    if not original_filename:
        return None

    ext = original_filename.split('.')[-1]
    filename = uuid.uuid4()
    full_filename = f"{filename}.{ext}"
    return f'{model_name}/{attr_name}/{filename}/{full_filename}'


def delete_std_images_from_media(std_image_file, variations):
    """
    Delete images which were created by StdImageField.

    :param std_image_file: instance of StdImageFile from django-stdimage library
    :param variations: iterable obj with names of declared variations for
                        std_image_file
    :return: None
    """
    if std_image_file and (
            isinstance(std_image_file, StdImageFieldFile) and
            os.path.isfile(std_image_file.path)):
        path = std_image_file.path.split(settings.MEDIA_DIR + '/')[-1]
        os.remove(os.path.join(settings.MEDIA_ROOT, path))
        for variant in variations:
            extension = path.split('.')[-1]
            filename = path.split('.')[-2]
            path_to_variant_file = f'{filename}.{variant}.{extension}'
            os.remove(
                os.path.join(settings.MEDIA_ROOT, path_to_variant_file))


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


class UploadedImageField(serializers.ImageField):
    """
    Class which converts a base64 string to a file when input
    and converts image by path to it into base64 string
    """

    def to_internal_value(self, data):
        if isinstance(data, UploadedFile):
            data = ContentFile(data.read(), name=data.name)
        if data == 'undefined':
            return None

        return super(UploadedImageField, self).to_internal_value(data)

    def to_representation(self, image_field):
        domain_site = self.context.get('domain')
        if not (image_field and domain_site):
            return ''

        domain = f'{PROTOCOL}://{str(domain_site)}'
        original_url = image_field.url
        variation = self.context['variation']
        if variation:
            extension = original_url.split('.')[-1]
            original_url = original_url.split('.')[0]
            image_url = f"{domain}{original_url}.{variation}.{extension}"
        else:
            image_url = f"{domain}{original_url}"

        return image_url


class HashIdField(serializers.Field):
    """
    Field for id for serializer
    """

    def to_representation(self, data):
        return settings.HASH_IDS.encode(data)

    def to_internal_value(self, data):
        try:
            user_id = settings.HASH_IDS.decode(data)[0]
        except IndexError:
            raise serializers.ValidationError('Invalid hashed_user_id')

        return super(HashIdField, self).to_internal_value(user_id)
