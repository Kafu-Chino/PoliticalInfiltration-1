from django.db import models


# Create your models here.
class SensitiveWord(models.Model):
    s_id = models.CharField(max_length=50, primary_key=True)
    prototype = models.CharField(max_length=50, blank=True, null=True)
    transform = models.CharField(max_length=50, blank=True, null=True)
    e_id = models.CharField(max_length=50, blank=True, null=True)
    perspective_bias = models.IntegerField(blank=True, null=True)

    class Meta():
        db_table = 'SensitiveWord'


class GlobalParameter(models.Model):
    p_name = models.CharField(max_length=50, primary_key=True)
    p_value = models.CharField(max_length=50, blank=True, null=True)
    p_instruction = models.CharField(max_length=50, blank=True, null=True)

    class Meta():
        db_table = 'GlobalParameter'


class EventParameter(models.Model):
    p_id = models.CharField(max_length=50, primary_key=True)
    p_name = models.CharField(max_length=50, blank=True, null=True)
    p_value = models.CharField(max_length=50, blank=True, null=True)
    e_id = models.CharField(max_length=50, blank=True, null=True)
    p_instruction = models.CharField(max_length=50, blank=True, null=True)

    class Meta():
        db_table = 'EventParameter'


class EventKeyWord(models.Model):
    k_id = models.CharField(max_length=50, primary_key=True)
    word = models.CharField(max_length=50, blank=True, null=True)
    e_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta():
        db_table = 'EventKeyWord'
