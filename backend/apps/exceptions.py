from rest_framework.exceptions import APIException, NotFound, PermissionDenied


class ValidationError(APIException):
    status_code = 422

