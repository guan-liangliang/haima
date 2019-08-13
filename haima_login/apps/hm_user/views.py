from django.shortcuts import render, redirect
from django.views.generic import View
import re
import json
from apps.hm_user.models import Hm_User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from haima_login import settings
from celery_tasks.tasks import send_register_active_email
from utli import aliyun
from django.core.cache import cache
from utli import restful
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login


#     登录
class Login(View):
    def get(self, request):
        hashkey = CaptchaStore.generate_key()    #手动添加
        image_url = captcha_image_url(hashkey)
        # register_form = RegisterFrom()     #自动生成
        # return render(request, 'login.html', {'register_form': register_form})

        if "username" in request.COOKIES:    #用户勾选功能：判断有没有用户
            username = request.COOKIES.get('username')
            checked = "checked"
        else:
            username = ""
            checked = ""
        return render(request, 'login.html', {'image_url': image_url, 'hashkey': hashkey,
                                              "username": username, "checked": checked})


    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        captcha_0 = request.POST.get('captcha_0')    #获取前端得hashkey
        # print(captcha_0)
        chapta_1 = request.POST.get('captcha_1')    #获取前端提交得验证码值
        # print(chapta_1)
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        if not all([username, password, chapta_1]):
            return render(request, 'login.html', {'error_msg': '信息不完整', 'image_url': image_url, 'hashkey': hashkey})
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if CaptchaStore.objects.filter(response=chapta_1, hashkey=captcha_0):   #图形验证码是否正确
                    login(request, user)
                    #记住用户名功能
                    response = redirect('hm_user:index')
                    remember = request.POST.get('remember')
                    if remember == 'on':   #on表示勾选了，将用户保存在cookie,过期时间7天
                        response.set_cookie("username", username, max_age=7*24*3600)
                    else:      #没有勾选删除cookie
                        response.delete_cookie('username')
                    return response
                else:
                    return render(request, 'login.html', {'error_msg': '图形验证码错误', 'image_url': image_url, 'hashkey': hashkey})
            else:

                return render(request, 'login.html', {'error_msg': '用户未激活', 'image_url': image_url, 'hashkey': hashkey})
        else:

            return render(request, 'login.html', {'error_msg': '账号密码不对', 'image_url': image_url, 'hashkey': hashkey})




#        注册
class Register(View):
    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        allow = request.POST.get('allow')
        code = request.POST.get('code')   #前端提交得验证码
        cache_code = cache.get(phone)   # 获取redis验证码

        if not all([username, password, email, phone]):
            return render(request, 'register.html', {"error_msg": "信息不完整"})
        if not re.match(r"^(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$", phone):
            return render(request, 'register.html', {"error_msg": "手机号格式不正确"})
        if allow != "yes":
            return render(request, 'register.html', {"error_msg": "请勾选同意"})
        if code != cache_code:
            return render(request, 'register.html', {"error_msg": "手机验证码错误"})
        try:
            user = Hm_User.objects.get(username=username)
        except Hm_User.DoesNotExist:
            user = None  #如果出现该异常说明用户不存在，则让user为空
        if user:
            return render(request, 'register.html', {"error_msg": "用户已经存在"})
        user = Hm_User.objects.create_user(username=username, password=password,
                                           email=email, phone=phone, is_active=0)

        #生成用户激活邮件得token，主要是为了加密id
        serializer = Serializer(settings.SECRET_KEY, 3600)  #有效期为1小时
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode()
        #发送邮件，clery异步发送
        send_register_active_email.delay(email, username, token)
        return redirect('hm_user:index')


class ActiveView(View):
    def get(self, request, token):
        #进行账户激活
        # 获取加密的serializer对象
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            #获取用户id
            user_id = info['confirm']
            #根据用户id获取该用户对象
            user = Hm_User.objects.get(id=user_id)
            #设置用户对象中的is_active字段值为1，激活
            user.is_active = 1
            user.save()
            #使用反向解析跳转到登陆界面
            return redirect('hm_user:login')
        except SignatureExpired as e:    #需要导入
            return HttpResponse("激活链接过期")

#发送短信接口
def sms_send(request):
    phone = request.GET.get('phone')
    code = aliyun.get_code(6, True)    #验证码
    cache.set(phone, code, 600)    #添加到redis里面
    result = aliyun.send_sms(phone, code)
    return HttpResponse(result)


#短信验证码验证接口
def sms_check(request):
    # 1.获取电话和手动输入的验证码
    phone = request.GET.get('phone')
    # print(phone)
    code = request.GET.get('code')
    # print(code)
    # 要先定义一个假的，要不然直接就是None,如果没有获取到redis里存储的验证码，也会是None,到时就会皮队成功
    cache_code = "1"
    #2.获取redis中保持的code
    if cache.has_key(phone):   #判断缓存中是否包含 phone 键
        # 获取redis验证码
        cache_code = cache.get(phone)
    # 3.判断返回数据
    if code == cache_code:
        # return HttpResponse(json.dumps({"result": 'True'}))
        return restful.ok("ok", data=None)
    else:
        # return HttpResponse(json.dumps({"result": 'False'}))
        return restful.params_error("验证码错误", data=None)



#图形验证码刷新
def img_refresh(request):
    if not request.is_ajax():
        return HttpResponse('不是ajax请求')
    new_kew = CaptchaStore.generate_key()
    to_json_response = {
        'hashkey': new_kew,
        'image_url': captcha_image_url(new_kew)
    }
    return HttpResponse(json.dumps(to_json_response))


#图形验证码的验证
def ima_check(request):
    if request.is_ajax():
        result = CaptchaStore.objects.filter(response=request.GET.get('response'),
                                            hashkey=request.GET.get('hashkey'))
        if result:
            data = {'status': 1}
        else:
            data = {'status': 0}
        return JsonResponse(data)
    else:
        data = {'status': 0}
        return JsonResponse(data)




class Index(View):
    def get(self, request):
        return render(request, 'index.html')

    def post(self, request):
        pass
