from django.db import models

# Create your models here.


class EventPositive(models.Model):
    e_id = models.CharField(max_length=50)
    text = models.CharField(max_length=400)
    vector = models.BinaryField(null=True)
    store_timestamp= models.BigIntegerField(null=True)
    store_type = models.IntegerField(default=0)    # 0是自动初始的，1是手动添加的，2是扩线添加的
    process_status = models.IntegerField(default=0)    # 是否已处理过字段
    class Meta():
        db_table = 'EventPositive'