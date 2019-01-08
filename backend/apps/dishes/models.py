from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from users.models import User



class Timing(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)


class AtomicTiming(models.Model):

    timing = models.ForeignKey(Timing, on_delete=models.CASCADE,
                               related_name='atomic_timings')
    seconds = models.IntegerField(validators=[MinValueValidator(10),
                                            MaxValueValidator(18000)])
    power = models.IntegerField(validators=[MinValueValidator(10),
                                            MaxValueValidator(100)])
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('created',)


class Dish(models.Model):

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    users = models.ManyToManyField(User, related_name='dishes')
    timings = models.ManyToManyField(Timing, related_name='dishes')

    class Meta:
        ordering = ('name',)



