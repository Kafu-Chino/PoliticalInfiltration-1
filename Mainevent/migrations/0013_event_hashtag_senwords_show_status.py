# Generated by Django 2.2.4 on 2020-02-22 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mainevent', '0012_auto_20200222_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='event_hashtag_senwords',
            name='show_status',
            field=models.IntegerField(default=0),
        ),
    ]