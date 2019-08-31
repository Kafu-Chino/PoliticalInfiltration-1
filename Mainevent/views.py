from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView


class Test(APIView):
    """测试页面"""

    def get(self, request):
        """获取"""
        return HttpResponse('Hello world')

    def post(self, request):
        """修改"""
        pass

    def put(self, request):
        """更新"""
        pass

    def delete(self, request):
        """删除"""
        pass
