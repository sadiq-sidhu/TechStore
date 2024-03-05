from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
import pyotp
from .forms import Myform

from django.contrib.auth import authenticate,login,logout
from .otp import send_otp
from .models import profile





# Create your views here.

def sign_up(request):
    if request.method=='POST':
      username=request.POST['username']
      email=request.POST['email']
      phone=request.POST['phone']
      DOB=request.POST['DOB']
      password1=request.POST['password1']
      password2=request.POST['password2']
      form=Myform(request.POST)
      
      if password1==password2:
          
          if User.objects.filter(username=username).exists():
              messages.warning(request, 'Username already exists')
              return redirect('sign_up')
          if User.objects.filter(email=email).exists():
              messages.warning(request, 'Email already exists')
              return redirect('sign_up')
          if User.objects.filter(profile__phone=phone).exists():
              messages.warning(request,'Phone number is already already exists')
              return redirect('sign_up')

          if form.is_valid():
              
              my_user=User.objects.create_user(password=password1,email=email,username=username,)
              
              my_user_profile=profile(user=my_user,phone=phone,DOB=DOB)
              
              my_user.save()
              my_user_profile.save()
              print('user sssss')
              request.session['username']=username
            
            
              send_otp(request,email)
              return redirect('otp')
          else: 
             messages.error(request,'Captcha Error')
        
      else:
          
          messages.error(request,'Password and Confirm Password not same')
          return redirect('sign_up')
      
    form=Myform()
    return render(request,'accounts/sign_up.html',{'form': form}) 



def otp(request):
    if request.method=='POST':
        otp=request.POST['otp']
        username=request.session['username']
        print(otp)
        otp_secret_key=request.session['otp_secret_key']
        otp_valid_date=request.session['otp_valid_date']
        if otp_secret_key and otp_valid_date is not None:
            print(otp,'1st',otp_valid_date)
            valid_date=datetime.fromisoformat(otp_valid_date)
            print('va',valid_date)
            if valid_date>datetime.now():
                print('valid date')
                totp=pyotp.TOTP(otp_secret_key, interval=600)
                print(totp)
                if totp.verify(otp):
                    print('totp verify')
            
                    del request.session['otp_secret_key']
                    del request.session['otp_valid_date']
                    user=get_object_or_404(User,username=username)
                    user.profile.is_verified=True
                    user.save()
                    user.profile.save()
                    print('ss=sf ')
                    del request.session['username']
                    return redirect('login')
            
                else:
                    messages.error(request,'Invalid OTP')   
            else:
                 messages.error(request,'OTP has expired.')
                 print('expired')   
        else:
             messages.error(request,'Oops..something went rong')     
                
                    
    
    return render(request,'accounts/otp.html')      

          

def log_in(request):
    # if User.is_authenticated:
    #     return redirect('home')
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user_obj=User.objects.filter(username=username)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.!!')
            return redirect('login')
        
        if not user_obj[0].profile.is_verified:
            messages.warning(request,'Your account is not OTP verified')
            return redirect('login')
        
        user=authenticate(request,username=username,password=password)
        
        if user is not None :
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Invalid Password or You are blocked')
            return redirect('login')
    
    return render(request,'accounts/login.html')

def log_out(request):
    logout(request)
    return redirect('login')

