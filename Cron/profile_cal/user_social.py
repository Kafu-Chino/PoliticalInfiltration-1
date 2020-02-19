import sys
import os
import time
import datetime
from collections import defaultdict
from data_get_utils import sql_select,sql_insert_many
from Config.db_utils import es
from elasticsearch.helpers import scan

def get_user_social(uidlist,date):
    