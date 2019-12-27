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
    uid = models.CharField(max_length=30)
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


class UserActivity(models.Model):
    ua_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=30, blank=True, null=True)
    statusnum = models.IntegerField(blank=True, null=True)
    timestamp = models.BigIntegerField(blank=True, null=True)
    send_ip = models.CharField(max_length=30, blank=True, null=True)
    geo = models.CharField(max_length=50, blank=True, null=True)
    store_date = models.DateField(blank=True, null=True)

    class Meta():
        db_table = 'UserActivity'


class UserBehavior(models.Model):
    ub_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=30, blank=True, null=True)
    originalnum = models.IntegerField(blank=True, null=True)
    commentnum = models.IntegerField(blank=True, null=True)
    retweetnum = models.IntegerField(blank=True, null=True)
    timestamp = models.BigIntegerField(blank=True, null=True)
    store_date = models.DateField(blank=True, null=True)

    class Meta():
        db_table = 'UserBehavior'


class Influence(models.Model):
    mid = models.CharField(max_length=30, primary_key=True)
    uid = models.CharField(max_length=30)
    comment = models.IntegerField()
    retweeted = models.IntegerField()
    original_retweeted_time_num = models.IntegerField()
    original_comment_time_num = models.IntegerField()
    original_retweeted_average_num = models.IntegerField()
    original_comment_average_num = models.IntegerField()
    timestamp = models.BigIntegerField()
    date = models.DateField()
    class Meta():
        db_table = 'Influence'

