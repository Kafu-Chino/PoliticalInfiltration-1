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
    main_domain = models.CharField(max_length=30,blank=True, null=True)
    domains = JSONField()
    timestamp = models.BigIntegerField()
    store_date = models.DateField(blank=True, null=True)
    class Meta():
        db_table = 'UserDomain'


class UserSocialContact(models.Model):
    uc_id = models.CharField(max_length=120, primary_key=True)
    
    target = models.CharField(max_length=30, null=True)
    target_name = models.CharField(max_length=50, null=True)
    source = models.CharField(max_length=30, null=True)
    source_name = models.CharField(max_length=50, null=True)
    message_type = models.IntegerField(default=2)
    count = models.IntegerField(default=0)
    timestamp = models.BigIntegerField(blank=True, null=True)
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
    ua_id = models.CharField(max_length=100, primary_key=True)
    uid = models.CharField(max_length=30, blank=True, null=True,db_index=True)
    statusnum = models.IntegerField(blank=True, null=True)
    sensitivenum = models.IntegerField(blank=True, null=True)
    timestamp = models.BigIntegerField(blank=True, null=True)
    send_ip = models.CharField(max_length=1000, blank=True, null=True)
    geo = models.CharField(max_length=200, blank=True, null=True)
    store_date = models.DateField(blank=True, null=True)

    class Meta():
        db_table = 'UserActivity'


class UserBehavior(models.Model):
    ub_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=30, blank=True, null=True,db_index=True)
    originalnum = models.IntegerField(blank=True, null=True)
    commentnum = models.IntegerField(blank=True, null=True)
    retweetnum = models.IntegerField(blank=True, null=True)
    sensitivenum = models.IntegerField(blank=True, null=True)
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



class WordCount(models.Model):
    uwc_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=30)
    wordcount = JSONField()
    timestamp = models.BigIntegerField()
    store_date = models.DateField(blank=True, null=True)
    class Meta():
        db_table = 'WordCount'


class UserSentiment(models.Model):
    us_id = models.CharField(max_length=50, primary_key=True)
    uid = models.CharField(max_length=30, blank=True, null=True,db_index=True)
    timestamp = models.BigIntegerField(blank=True, null=True)
    negtive = models.IntegerField(blank=True, null=True)
    nuetral = models.IntegerField(blank=True, null=True)
    positive = models.IntegerField(blank=True, null=True)
    store_date = models.DateField(blank=True, null=True)

    class Meta():
        db_table = 'UserSentiment'


class UserInfluence(models.Model):
    uid = models.CharField(max_length=30, blank=True,primary_key=True)
    timestamp = models.BigIntegerField(blank=True, null=True)
    influence = models.IntegerField(blank=True, null=True)
    importance = models.IntegerField(blank=True, null=True)
    activity = models.IntegerField(blank=True, null=True)
    sensitity = models.IntegerField(blank=True, null=True)
    store_date = models.DateField(blank=True, null=True)

    class Meta():
        db_table = 'UserInfluence'

class NewUserInfluence(models.Model):
    uid_ts = models.CharField(max_length=40, primary_key=True)
    uid = models.CharField(max_length=30, blank=True,db_index=True)
    timestamp = models.BigIntegerField(blank=True, null=True)
    influence = models.IntegerField(blank=True, null=True)
    importance = models.IntegerField(blank=True, null=True)
    activity = models.IntegerField(blank=True, null=True)
    sensitity = models.IntegerField(blank=True, null=True)
    store_date = models.DateField(blank=True, null=True)

    class Meta():
        db_table = 'NewUserInfluence'