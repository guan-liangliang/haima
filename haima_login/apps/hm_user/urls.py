from django.urls import path
from apps.hm_user import views

app_name = 'hm_user'
urlpatterns = [
    path('index/', views.Index.as_view(), name='index'),   #首页
    path('login/', views.Login.as_view(), name='login'),   #登录
    path('register', views.Register.as_view(), name='register'),  #注册
    path('active/<token>/', views.ActiveView.as_view(), name='active'),  #邮箱激活账号
    path('sms_send/', views.sms_send, name='sms_send'),  # 发送短信接口
    path('sms_check/', views.sms_check, name='sms_check'),  # 短信验证码验证接口
    path('img_refresh/', views.img_refresh, name='img_refresh'),  # 图形验证码刷新接口
    path('ima_check/', views.ima_check, name='ima_check'),  # 图形验证码验证接口

]