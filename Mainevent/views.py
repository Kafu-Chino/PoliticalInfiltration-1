from django.http import JsonResponse, HttpResponse

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema

class Test(APIView):
    """测试页面"""
    def get(self, request):
        """获取用户信息"""
        # do something
        return HttpResponse('Hello world')

    def post(self, request):
        """获取用户信息"""
        pass

    def put(self, request):
        """更新用户信息"""
        pass

    def delete(self, request):
        """删除用户信息"""
        pass

