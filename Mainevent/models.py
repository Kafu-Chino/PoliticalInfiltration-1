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
    computestatus = models.IntegerField(default=0)  # 计算状态：0为未计算，1为计算中，2为计算完成
    monitorstatus = models.IntegerField(default=1)  # 监测状态：0为未在监测，1为监测中
    identitystatus = models.IntegerField(default=0)  # 确认状态：0为未确认为敏感用户，1为已确认
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
    add_manully = models.BooleanField(null=True,default=0)

    class Meta():
        db_table = 'Information'

class Event(models.Model):
    e_id = models.CharField(max_length=100, primary_key=True)
    event_name = models.CharField(max_length=50)
    keywords_dict = models.CharField(max_length=100)   # 为查询表达式
    begin_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    es_index_name = models.CharField(max_length=100, null=True)
    cal_status = models.IntegerField(default=0)
    monitor_status = models.IntegerField(default=1)
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
    user_count = models.IntegerField(default=0)
    weibo_count = models.IntegerField(default=0)
    geo_inland = JSONField()
    geo_outland = JSONField()
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