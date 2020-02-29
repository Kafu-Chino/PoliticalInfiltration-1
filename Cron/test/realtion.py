#-*-coding=utf-8-*-
import sys
import os
import time
import datetime
import json
import pymysql
import django
from elasticsearch.helpers import scan
from collections import defaultdict
from data_utils import sql_insert_many


sys.path.append("../../")
os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()

from Config.db_utils import es, pi_cur, conn
from Mainevent.models import Event, Figure, Information

cursor = pi_cur()

item = Event.objects.get(e_id="xianggangshijian_1581919160")#查找Book表要修改的id对象
objs = Information.objects.filter(add_manully=0)#查找Author表对应id的多个obj
item.information.set(objs)    #-------修改多对多字段 