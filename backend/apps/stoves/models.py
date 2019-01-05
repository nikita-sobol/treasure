from django.db import models
from users.models import User


class Stove(models.Model):
    serial_id = models.CharField(max_length=32)
    name = models.CharField(max_length=50, blank=True)


class Cook(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             related_name='as_cook')
    stove = models.ForeignKey(Stove, related_name='cooks',
                              on_delete=models.CASCADE)

    is_chief = models.BooleanField(default=False)
