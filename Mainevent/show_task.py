from django.http import JsonResponse
from Mainevent.models import Task
from django.core import serializers
import json

def show(request):
	result = Task.objects.filter()
	json_data = serializers.serialize("json",result)
	results = json.loads(json_data)
	return JsonResponse(results,safe=False)


