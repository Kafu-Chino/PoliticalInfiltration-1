import sys
import os
import django
sys.path.append('../../../')

os.environ['DJANGO_SETTINGS_MODULE'] = 'PoliticalInfiltration.settings'
django.setup()  # 启动django

from Mainevent.models import *

# from Config.base import es, redis_ep

def test_push_redis():
	# dic = {k:500000-k for k in range(500000)}
	# l = [i for i in range(100)]
	# print('over')
	# print(redis_ep.mget(l))
	# redis_ep.delete(*redis_ep.keys())
	# print(redis_ep.keys())
	print("nothing happened.")

if __name__ == '__main__':
	test_push_redis()