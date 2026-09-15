from django import forms
# from captcha.fields import ReCaptchaField 
# from captcha.widgets import ReCaptchaV2Checkbox

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

class Myform(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

