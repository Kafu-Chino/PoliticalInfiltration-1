from django.db import models

# Create your models here.


class EventPositive(models.Model):
    e_id = models.CharField(max_length=50)
    text = models.CharField(max_length=400)
    vector = models.BinaryField(null=True)
    store_timestamp= models.BigIntegerField(null=True)
    store_type = models.IntegerField(default=0)    # 0是自动初始的，1是手动添加的，2是扩线添加的
    process_status = models.IntegerField(default=0)    # 是否已处理过字段 0未处理 1处理完毕  
    class Meta():
        db_table = 'EventPositive'


class ExtendReview(models.Model):
    ie_id = models.CharField(max_length=100, primary_key=True)
    e_id = models.CharField(max_length=50)
    uid = models.CharField(max_length=50)
    root_uid = models.CharField(max_length=50)
    mid = models.CharField(max_length=50)
    root_mid = models.CharField(max_length=50,null=True)
    text = models.CharField(max_length=400,null=True)
    timestamp = models.BigIntegerField(null=True)
    send_ip = models.CharField(max_length=20,null=True)
    geo = models.CharField(max_length=50,null=True)
    message_type = models.IntegerField(null=True)
    source = models.CharField(max_length=20,null=True)
    process_status = models.IntegerField(default=0)    # 是否已处理过字段 0未处理 1处理完毕 

    class Meta():
        db_table = 'ExtendReview'


class ExtendTask(models.Model):
    e_id = models.CharField(max_length=50, primary_key=True)
    cal_status = models.IntegerField(default=0)    # 计算状态 0是未计算 1是计算中 2是计算完成 3是处理完毕

    class Meta():
        db_table = 'ExtendTask'