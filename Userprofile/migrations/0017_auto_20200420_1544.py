# Generated by Django 2.2.4 on 2020-04-20 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Userprofile', '0016_auto_20200420_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersentiment',
            name='uid',
            field=models.CharField(blank=True, db_index=True, max_length=30, null=True),
        ),
    ]