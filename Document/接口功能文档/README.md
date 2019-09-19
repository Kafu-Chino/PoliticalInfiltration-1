# 接口功能文档
放置后台与前端衔接的接口功能说明文档，方便查阅接口逻辑和功能，便于维护，可用接口API生成
# 书写格式
在get/post等方法的下面写上三引号的注释，接口文档后方会自动跟上该接口的说明，参数等更多的设置有兴趣请自行学习实践一下
```python3
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
```