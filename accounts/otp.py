import pyotp
from datetime import datetime,timedelta
from django.core.mail import send_mail
from django.conf import settings



def send_otp(request,mail):
    totp=pyotp.TOTP(pyotp.random_base32(),interval=600)
    otp=totp.now()
    request.session['otp_secret_key']=totp.secret
    valid_date=datetime.now()+timedelta(minutes=10)
    request.session['otp_valid_date']=str(valid_date)
    
    
    subject = 'Please verify One Time Password!!'
 
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [mail]   
    send_mail( subject, f"Thank you for registering to our sit. \n Your One time password is ' {otp} '. its valid only under 10 minutes", email_from, recipient_list )
    print(f'OTP   {otp}')