from django.http import JsonResponse

class HttpCode(object):
    ok = 200
    paramserror = 400
    methoderror = 405
    servererror = 500


def result(code=HttpCode.ok, message="", data=None, kwargs=None):
    json_dict = {"code": code, "message": "", "result": ""}
    if kwargs and isinstance(kwargs,dict) and kwargs.keys():
        json_dict.update(kwargs)
    return JsonResponse(json_dict, json_dumps_params={"ensure_ascii": False})


def ok(message, data=None):
    return result(code=HttpCode.ok, message=message, data=data)

def params_error(message="", data=None):
    return result(code=HttpCode.paramserror, message=message, data=data)

def method_error(message='', data=None):
    return result(code=HttpCode.methoderror, message=message, data=data)

def server_error(message='', data=None):
    return result(code=HttpCode.servererror, message=message, data=data)

