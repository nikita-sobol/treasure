from rest_framework import serializers

from .models import Dish, Timing, AtomicTiming


class AtomicTimingSerializer(serializers.ModelSerializer):

    class Meta:
        model = AtomicTiming
        fields = ('seconds', 'power')


class TimingSerializer(serializers.ModelSerializer):
    atomic_timings = AtomicTimingSerializer(many=True, read_only=False)

    def create(self, validated_data):

        db_timing = Timing.objects.create(name=validated_data['name'])
        db_timing.dishes.add(validated_data['dish'])

        for atomic_timing in validated_data.get('atomic_timings', ()):
            AtomicTiming.objects.create(
                seconds=atomic_timing['seconds'],
                power=atomic_timing['power'],
                timing=db_timing
            )

        return db_timing

    class Meta:
        model = Timing
        fields = ('id', 'name', 'atomic_timings')


class DishSerializer(serializers.ModelSerializer):
    timings = TimingSerializer(many=True, read_only=False)

    def create(self, validated_data):

        db_dish = Dish.objects.create(
            name=validated_data['name'],
            description=validated_data.get('description', '')
        )

        db_dish.users.add(validated_data['cook'])

        for timing in validated_data.get('timings', ()):

            db_timing = Timing.objects.create(name=timing['name'])
            db_timing.dishes.add(db_dish)

            for atomic_timing in timing.get('atomic_timings', ()):
                AtomicTiming.objects.create(
                    seconds=atomic_timing['seconds'],
                    power=atomic_timing['power'],
                    timing=db_timing
                )

        return db_dish

    class Meta:
        model = Dish
        fields = ('id', 'name', 'description', 'timings')

