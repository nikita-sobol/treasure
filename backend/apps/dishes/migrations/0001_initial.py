# Generated by Django 2.1.4 on 2019-01-01 23:11

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AtomicTiming',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seconds', models.IntegerField()),
                ('power', models.IntegerField()),
                ('created', models.DateTimeField(default=datetime.datetime(2019, 1, 1, 23, 11, 44, 525029, tzinfo=utc))),
            ],
            options={
                'ordering': ('created',),
            },
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Timing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='dish',
            name='timings',
            field=models.ManyToManyField(to='dishes.Timing'),
        ),
        migrations.AddField(
            model_name='atomictiming',
            name='timing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atomic_timings', to='dishes.Timing'),
        ),
    ]
