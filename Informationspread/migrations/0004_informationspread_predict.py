# Generated by Django 2.2.4 on 2020-03-09 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Informationspread', '0003_informationspread_message_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='informationspread',
            name='predict',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
