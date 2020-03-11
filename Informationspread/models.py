from django.db import models


# Create your models here.
class Informationspread(models.Model):
    is_id = models.CharField(max_length=128, primary_key=True)
    mid = models.CharField(max_length=30, blank=True, null=True)
    comment_count = models.IntegerField(blank=True, null=True)
    retweet_count = models.IntegerField(blank=True, null=True)
    timestamp = models.BigIntegerField(blank=True, null=True)
    store_date = models.DateField(blank=True, null=True)
    hazard_index = models.FloatField(blank=True, null=True)
    message_type = models.IntegerField(blank=True, null=True)
    predict = models.BooleanField(blank=True,null=True)

    class Meta():
        db_table = 'Informationspread'
