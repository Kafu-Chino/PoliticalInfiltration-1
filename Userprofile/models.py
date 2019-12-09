from django.db import models

# Create your models here.


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
