# Generated by Django 4.1.2 on 2022-11-26 01:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photosharingapp', '0003_alter_profile_photo_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='date_created',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='followers',
            name='date_created',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='like',
            name='date_created',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='post',
            name='date_created',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='profile',
            name='date_created',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
