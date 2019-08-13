''' 短信下发核心方法
1. send_sms 发短信
2. get_code 生成验证码 '''
# coding=utf-8
import random
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

'''发送短信(手机,6位验证码)'''


def send_sms(phone, code):
    # !/usr/bin/env python
    # coding=utf-8

    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    client = AcsClient('LTAIznxYom8fTE24', '4eTEzXNBG3VW8iRfPZ1M8CDusiXDWU', 'cn-hangzhou')

    code = "{'code':'%s'}" % (code)
    # print(code)
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')  # https | http
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', phone)
    request.add_query_param('SignName', "关家实践组")
    request.add_query_param('TemplateCode', "SMS_172205443")
    request.add_query_param('TemplateParam', code)

    response = client.do_action(request)
    # python2:  print(response)
    # print(str(response, encoding='utf-8'))
    return str(response, encoding='utf-8')

'''生成随机验证码: 数字表示生成几位,   True表示生成带有字母的  False不带字母的'''


def get_code(n=6, alpha=True):
    s = ''  # 创建字符串变量,存储生成的验证码
    for i in range(n):  # 通过for循环控制验证码位数
        num = random.randint(0, 9)  # 生成随机数字0-9
        if alpha:  # 需要字母验证码,不用传参,如果不需要字母的,关键字alpha=False
            upper_alpha = chr(random.randint(65, 90))
            lower_alpha = chr(random.randint(97, 122))
            num = random.choice([num, upper_alpha, lower_alpha])
            s = s + str(num)

    return s


if __name__ == '__main__':
    # 调用下发短信方法
    # send_sms('18234686259', get_code(4, True))
    print(get_code(6, False))  # 打印6位数字验证码
    print(get_code(6, True))  # 打印6位数字字母混合验证码
    print(get_code(4, False))  # 打印4位数字验证码
    print(get_code(4, True))  # 打印4位数字字母混合验证码

