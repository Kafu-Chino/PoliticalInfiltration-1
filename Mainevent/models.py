from django.db import models


# Create your models here.
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
    class Meta():
        db_table = 'Event'

class Figure(models.Model):
    f_id = models.CharField(max_length=30, primary_key=True)
    gender = models.NullBooleanField()#True:male，Fales：female,Null：empty
    follow_num = models.IntegerField(blank=True, null=True)
    fans_num = models.IntegerField(blank=True, null=True)
    tweets_num = models.IntegerField(blank=True, null=True)
    authentication = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    event = models.ManyToManyField('Event')
    class Meta():
        db_table = 'Figure'

class Information(models.Model):
    i_id = models.CharField(max_length=30, primary_key=True)
    uid = models.CharField(max_length=30)
    root_uid = models.CharField(max_length=30)
    mid = models.CharField(max_length=30)
    comment = models.IntegerField()
    retweeted = models.IntegerField()
    text = models.CharField(max_length=400)
    keywords_dict = models.CharField(max_length=100)
    timestamp = models.BigIntegerField()
    date = models.DateField()
    ip = models.CharField(max_length=20)
    geo = models.CharField(max_length=50)
    message_type = models.IntegerField()
    root_mid = models.CharField(max_length=30)
    source = models.CharField(max_length=20)
    i_level = models.IntegerField()
    event = models.ManyToManyField('Event')
    class Meta():
        db_table = 'Information'

class Hot_post(models.Model):
    h_id = models.CharField(max_length=30, primary_key=True)
    uid = models.CharField(max_length=30)
    root_uid = models.CharField(max_length=30)
    mid = models.CharField(max_length=30)
    comment = models.IntegerField()
    retweeted = models.IntegerField()
    text = models.CharField(max_length=400)
    keywords_dict = models.CharField(max_length=100)
    timestamp = models.BigIntegerField()
    date = models.DateField()
    ip = models.CharField(max_length=20)
    geo = models.CharField(max_length=50)
    message_type = models.IntegerField()
    root_mid = models.CharField(max_length=30)
    source = models.CharField(max_length=20)
    store_timestamp = models.BigIntegerField()
    store_date = models.DateField()
    class Meta():
        db_table = 'Hot_post'

class Task(models.Model):
    t_id = models.CharField(max_length=30, primary_key=True)
    task_type = models.IntegerField()
    into_type = models.IntegerField()
    status = models.IntegerField()
    e_id = models.CharField(max_length=100, blank=True, null=True)
    uid = models.CharField(max_length=30, blank=True, null=True)
    root_uid = models.CharField(max_length=30, blank=True, null=True)
    mid = models.CharField(max_length=30, blank=True, null=True)
    comment = models.IntegerField(blank=True, null=True)
    retweeted = models.IntegerField(blank=True, null=True)
    text = models.CharField(max_length=400)
    keywords_dict = models.CharField(max_length=100)
    timestamp = models.BigIntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    ip = models.CharField(max_length=20, blank=True, null=True)
    geo = models.CharField(max_length=50, blank=True, null=True)
    message_type = models.IntegerField(blank=True, null=True)
    root_mid = models.CharField(max_length=30, blank=True, null=True)
    source = models.CharField(max_length=20)
    into_timestamp = models.BigIntegerField()
    into_date = models.DateField()
    class Meta():
        db_table = 'Task'
