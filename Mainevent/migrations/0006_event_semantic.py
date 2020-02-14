# Generated by Django 2.2.4 on 2020-02-14 10:46

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('Mainevent', '0005_auto_20200211_0325'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event_Semantic',
            fields=[
                ('es_id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('e_id', models.CharField(blank=True, max_length=30, null=True)),
                ('e_name', models.CharField(max_length=50)),
                ('topics', django_mysql.models.JSONField(default=dict)),
                ('timestamp', models.BigIntegerField(blank=True, null=True)),
                ('into_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Event_Semantic',
            },
        ),
    ]
