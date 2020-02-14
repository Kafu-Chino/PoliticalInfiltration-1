from django.db import models
from django_mysql.models import JSONField

# Create your models here.
class Figure(models.Model):
    f_id = models.CharField(max_length=30, primary_key=True)
    uid = models.CharField(max_length=30, blank=True, null=True)
    nick_name = models.CharField(max_length=50, blank=True, null=True)
    create_at = models.CharField(max_length=50, blank=True, null=True)
    user_birth = models.CharField(max_length=50, blank=True, null=True)
    political = models.CharField(max_length=30, blank=True, null=True)
    domain = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    sex = models.NullBooleanField()  # True:male，Fales：female,Null：empty
    friendsnum = models.IntegerField(blank=True, null=True)
    fansnum = models.IntegerField(blank=True, null=True)
    computestatus = models.IntegerField(blank=True, null=True)
    monitorstatus = models.IntegerField(blank=True, null=True)
    into_date = models.DateField(blank=True, null=True)
    user_location = models.CharField(max_length=100, blank=True, null=True)

    class Meta():
        db_table = 'Figure'


class Information(models.Model):
    i_id = models.CharField(max_length=30, primary_key=True)
    uid = models.CharField(max_length=30)
    root_uid = models.CharField(max_length=30)
    mid = models.CharField(max_length=30)
    root_mid = models.CharField(max_length=30,null=True)
    text = models.CharField(max_length=400,null=True)
    timestamp = models.BigIntegerField(null=True)
    send_ip = models.CharField(max_length=20,null=True)
    geo = models.CharField(max_length=50,null=True)
    message_type = models.IntegerField(null=True)
    source = models.CharField(max_length=20,null=True)
    hazard_index = models.FloatField(blank=True, null=True)
    cal_status = models.IntegerField(default=0)
    monitor_status = models.IntegerField(default=1)

    class Meta():
        db_table = 'Information'

class Event(models.Model):
    e_id = models.CharField(max_length=30, primary_key=True)
    event_name = models.CharField(max_length=50)
    keywords_dict = models.CharField(max_length=100)
    begin_timestamp = models.BigIntegerField()
    begin_date = models.DateField()
    end_timestamp = models.BigIntegerField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    content = models.CharField(max_length=400)
    uid = models.CharField(max_length=30, blank=True, null=True)
    status = models.IntegerField(default=1)
    if_manul = models.IntegerField(default=0)
    information = models.ManyToManyField(Information, related_name="event")
    figure = models.ManyToManyField(Figure, related_name="event")

    class Meta():
        db_table = 'Event'


class Event_Analyze(models.Model):
    e_id = models.CharField(max_length=30, primary_key=True)
    event_name = models.CharField(max_length=50)
    hot_index = JSONField()
    sensitive_index = JSONField()
    negative_index = JSONField()
    into_date = models.DateField(blank=True, null=True)
    class Meta():
        db_table = 'Event_Analyze'


class Event_Semantic(models.Model):
    es_id = models.CharField(max_length=30, primary_key=True)
    e_id = models.CharField(max_length=30, blank=True, null=True)
    e_name = models.CharField(max_length=50)
    topics = JSONField()
    timestamp = models.BigIntegerField(blank=True, null=True)
    into_date = models.DateField(blank=True, null=True)
    class Meta():
        db_table = 'Event_Semantic'