# -*- coding: utf-8 -*-

from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
import hashlib

from .models import *

from rest_framework.views import APIView
from rest_framework.schemas import ManualSchema


class User_Info(APIView):
    """查询符合条件用户信息接口"""

    def get(self, request):
        """
        判断当前登录用户是否是权限为1或权限为2的非普通用户，是则查询User数据库，返回查询用户信息（如未设查询条件则查询所有），用户名和权限;否则，返回提示无权限
        格式: {"status":1,"result":[{"username": username, "role": role},{},...]};
              {"status":0,"result":"无匹配结果！"};
              {"status":0,"result":"请先登录！"};
              {"status":0,"result":"暂无权限查看！"}
        """
        d = {1: "超级管理员", 2: "管理员", 3: "普通用户"}
        res_dict = {}
        try:
            if request.session['role'] == 1 or request.session['role'] == 2:
                keyword = request.GET.get('keyword')
                if not keyword:
                    result = list(User.objects.all().values("username", "role"))
                else:
                    result = list(User.objects.filter(username__contains=keyword).values("username", "role"))
                if len(result) > 0:
                    res_dict["status"] = 1
                    for item in result:
                        item["role"] = d[item["role"]]
                        res_dict["result"] = result
                else:
                    res_dict["status"] = 0
                    res_dict["result"] = "无匹配结果！"
            else:
                res_dict["status"] = 0
                res_dict["result"] = "暂无权限查看！"
        except:
            res_dict["status"] = 0
            res_dict["result"] = "请先登录！"

        return JsonResponse(res_dict)


class User_Login(APIView):
    """用户登录接口"""

    def post(self, request):
        """
        获取username，password，判断是否有效并与数据库匹配，成功后添加到session中，并重定向至首页
        """
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.password == hash_code(password):
                if request.session.get('username', None) == username:
                    message = "您已登录！"
                    return JsonResponse({"message": message})
                request.session['username'] = user.username
                request.session['role'] = user.role
                request.session['is_login'] = True
                message = "登录成功！"
                return JsonResponse({"message": message})
            else:
                message = "密码不正确！"
        except:
            message = "用户不存在！"
        return JsonResponse({"message": message})


class User_Logout(APIView):
    """用户登出接口"""

    def get(self, request):
        """
        清空session，重定向至登录页面
        """
        if request.session.get("is_login", None):
            request.session.flush()
        return JsonResponse({"status": "已登出"})


class User_Add(APIView):
    """添加用户接口"""

    def post(self, request):
        """
        判断当前登录用户是否是权限为1或权限为2的非普通用户，是则添加用户至数据库，返回添加成功;否则，返回提示无权限
        格式: {"status":1,"message":"添加成功"};
              {"status":0,"message":"暂无操作权限！"};
              {"status":0,"message":"请先登录！"};
              {"status":0,"message":"用户已存在！"}
        """
        res_dict = {}
        try:
            if request.session['role'] == 1 or request.session['role'] == 2:
                username = request.POST.get('username')
                if not User.objects.filter(username=username).first():
                    password = request.POST.get('password')
                    role = request.POST.get('role')
                    User.objects.create(username=username, password=hash_code(password), role=role)
                    res_dict["status"] = 1
                    res_dict["message"] = "添加成功！"
                else:
                    res_dict["status"] = 0
                    res_dict["message"] = "用户已存在！"
            else:
                res_dict["status"] = 0
                res_dict["message"] = "暂无操作权限！"
        except:
            res_dict["status"] = 0
            res_dict["message"] = "请先登录！"
        return JsonResponse(res_dict)


class User_Delete(APIView):
    """删除用户接口"""

    def get(self, request):
        """
        判断当前登录用户是否是权限为1或权限为2的非普通用户，是则获取username,查询是否存在，执行删库操作，返回删除成功;
        否则，返回提示无权限
        格式: {"status":1,"message":"删除成功"};
              {"status":0,"message":"请先登录！"};
              {"status":0,"message":"暂无操作权限！"}
        """
        res_dict = {}
        username = request.GET.get('username')
        try:
            if request.session['role'] == 1 or request.session['role'] == 2:
                User.objects.filter(username=username).delete()
                res_dict["status"] = 1
                res_dict["message"] = "删除成功！"
            else:
                res_dict["status"] = 0
                res_dict["message"] = "暂无操作权限！"
        except:
            res_dict["status"] = 0
            res_dict["message"] = "请先登录！"
        return JsonResponse(res_dict)


class User_Modify(APIView):
    """更改用户信息接口"""

    def post(self, request):
        """
        判断当前登录用户是否是权限为1或权限为2的非普通用户，是则获取username,查询是否存在，执行改库操作，返回更改信息成功;
        否则，返回提示无权限
        格式: {"status":1,"message":"更改信息成功"};
              {"status":0,"message":"用户名已存在！"};
              {"status":0,"message":"该用户不存在！"};
              {"status":0,"message":"请先登录！"};
              {"status":0,"message":"暂无操作权限！"}
        """
        res_dict = {}
        username = request.POST.get('username')
        try:
            if request.session['role'] == 1 or request.session['role'] == 2:
                user = User.objects.filter(username=username).first()
                if user:
                    new_username = request.POST.get('new_username') if request.POST.get(
                        'new_username') else user.username
                    new_role = request.POST.get('new_role') if request.POST.get('new_role') else user.role
                    new_pwd = hash_code(request.POST.get('new_pwd')) if request.POST.get('new_pwd') else user.password
                    if username == new_username:
                        User.objects.filter(username=username).update(password=new_pwd, role=new_role)
                        res_dict["status"] = 1
                        res_dict["message"] = "修改信息成功！"
                    elif not User.objects.filter(username=new_username).first():
                        User.objects.filter(username=username).update(username=new_username, password=new_pwd,
                                                                      role=new_role)
                        res_dict["status"] = 1
                        res_dict["message"] = "修改信息成功！"
                    else:
                        res_dict["status"] = 0
                        res_dict["message"] = "用户名已存在！"
                else:
                    res_dict["status"] = 0
                    res_dict["message"] = "该用户不存在！"
            else:
                res_dict["status"] = 0
                res_dict["message"] = "暂无操作权限！"
        except:
            res_dict["status"] = 0
            res_dict["message"] = "请先登录！"
        return JsonResponse(res_dict)


class User_Status(APIView):
    """返回用户登陆状态及权限接口"""

    def get(self, request):
        """
        根据前端传来的username，返回该用户登录状态及权限
        格式: 格式: {"status":1/0,"role":1/2/3, "message":"该用户不存在！"}
        """
        res_dict = {}
        username = request.GET.get('username')
        try:
            role = User.objects.filter(username=username).first().role
            if request.session.get("username", None) == username:
                status = 1
            else:
                status = 0
            res_dict["status"] = status
            res_dict["role"] = role
        except:
            message = "该用户不存在！"
            res_dict["message"] = message

        return JsonResponse(res_dict)


# 密码加密
def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()
