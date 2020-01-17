from django.db import models


# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=256, blank=True, null=True)
    role = models.IntegerField(blank=True, null=True)

    class Meta():
        db_table = 'User'
