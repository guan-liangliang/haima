from django import forms
from captcha.fields import CaptchaField


class RegisterFrom(forms.Form):
    captcha = CaptchaField()