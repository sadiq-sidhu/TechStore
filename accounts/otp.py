import pyotp
from datetime import datetime,timedelta
from django.core.mail import send_mail
from django.conf import settings



def send_otp(request,mail):
    totp=pyotp.TOTP(pyotp.random_base32(),interval=180)
    otp=totp.now()
    request.session['otp_secret_key']=totp.secret
    valid_date=datetime.now()+timedelta(minutes=3)
    request.session['otp_valid_date']=str(valid_date)
    request.session['signup_email']=mail
    request.session['otp_resend_allowed']=str(datetime.now()+timedelta(minutes=1))
    
    
    subject = 'Please verify One Time Password!!'

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [mail]  
    print(f'OTP   {otp}')
    try:  
        send_mail( subject, f"Thank you for registering with TechStore. \n Your One time password is '{otp}'. its valid only under 3 minutes", email_from, recipient_list )
    except Exception as e:
        raise