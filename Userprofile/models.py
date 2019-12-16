from django.db import models
from django_mysql.models import JSONField

# Create your models here.
class UserTopic(models.Model):
    ut_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=30)
    topics = JSONField()
    timestamp = models.BigIntegerField()
    store_date = models.DateField(blank=True, null=True)
    class Meta():
        db_table = 'UserTopic'

class UserDomain(models.Model):
    ud_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=30)
    domains = JSONField()
    timestamp = models.BigIntegerField()
    store_date = models.DateField(blank=True, null=True)
    class Meta():
        db_table = 'UserDomain'


class UserSocialContact(models.Model):
    uc_id = models.CharField(max_length=100, primary_key=True)
    target = models.CharField(max_length=30)
    target_name = models.CharField(max_length=50)
    source = models.CharField(max_length=30)
    source_name = models.CharField(max_length=50)
    message_type = models.IntegerField()
    #count = models.IntegerField()
    timestamp = models.BigIntegerField()
    store_date = models.DateField(blank=True, null=True)
    class Meta():
        db_table = 'UserSocialContact'

class UserKeyWord(models.Model):
    ukw_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=30)
    keywords = JSONField()
    hastags = JSONField()
    sensitive_words = JSONField()
    timestamp = models.BigIntegerField()
    store_date = models.DateField(blank=True, null=True)
    class Meta():
        db_table = 'UserKeyWord'
