from django.db import models
from django.utils import timezone


class Timing(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)


class AtomicTiming(models.Model):

    timing = models.ForeignKey(Timing, on_delete=models.CASCADE,
                               related_name='atomic_timings')
    seconds = models.IntegerField()
    power = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('created',)


class Dish(models.Model):

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    timings = models.ManyToManyField(Timing)

    class Meta:
        ordering = ('name',)



