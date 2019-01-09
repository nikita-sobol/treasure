from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Cook


class CookSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=False)

    class Meta:
        model = Cook
        fields = ('id', 'user', 'is_chief')

