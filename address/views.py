import os
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from .forms import CustomerAddressForm
from .models import Address
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from . validate import username_validation
from django.core.exceptions import ValidationError
from accounts.otp import send_otp
import pyotp
from django.utils import timezone
from datetime import timedelta

# Create your views here.
@method_decorator(login_required,name='dispatch')
class AddAddress(View):
    def get(self,request):
        form=CustomerAddressForm()
        context={
            'form':form
        }
        return render(request, 'address/AddAddress.html',context)
       
    def post(self,request):
        form=CustomerAddressForm(request.POST)
        if form.is_valid():
            user=request.user
            name=form.cleaned_data['name']
            mobile=form.cleaned_data['mobile'] 
            type=form.cleaned_data['type'] 
            locality=form.cleaned_data['locality'] 
            city=form.cleaned_data['city'] 
            state=form.cleaned_data['state'] 
            zip_code=form.cleaned_data['zip_code'] 
            
            reg=Address(user=user,type=type,name=name,locality=locality,city=city,zip_code=zip_code,state=state,mobile=mobile)
            reg.save()
            messages.success(request,"Congratulation! Profile save Successfully")
        else:
            messages.warning(request,"Invalid Input Data.!")
        context={'form':form}
        return render(request, 'address/AddAddress.html',context)
    
    
@login_required   
def ViewAddress(request):
    user=request.user
    address=Address.objects.filter(user=user)
    context={
        'address':address
    } 
    return render(request,'address/ViewAddress.html',context)

@method_decorator(login_required,name='dispatch')
class UpdateAddress(View):
    def get(self,request,pk):
        add=Address.objects.get(uid=pk)
        form=CustomerAddressForm(instance=add)
        context={'form':form}
        return render(request,'address/UpdateAddress.html',context)
    def post(self,request,pk):
        form=CustomerAddressForm(request.POST)
        if form.is_valid():
            add=Address.objects.get(uid=pk)
            
            add.name=form.cleaned_data['name']
            add.mobile=form.cleaned_data['mobile'] 
            add.type=form.cleaned_data['type'] 
            add.locality=form.cleaned_data['locality'] 
            add.city=form.cleaned_data['city'] 
            add.state=form.cleaned_data['state'] 
            add.zip_code=form.cleaned_data['zip_code'] 
            add.save()
            messages.success(request,"Congratulation! Profile updated Successfully")
        else:
            messages.warning(request,"Invalid Input Data.!")
        context={'form':form}
        return render(request,'address/UpdateAddress.html',context)

@login_required    
def Delete(request,pk):
    obj=Address.objects.get(uid=pk)
    obj.delete()
    return redirect('view_address')


@login_required
def profile(request):
    user=request.user
    print(user.username,user.id)
      
    if request.method=='POST':
        if len(request.FILES)!=0:
            if user.profile.profile_image:
              os.remove(user.profile.profile_image.path) 
            user.profile.profile_image= request.FILES['img']
        username=request.POST['username']
        phone=request.POST['phone']
        DOB=request.POST['dob']
        
        try:
            username_validation(username)
            # its a custom validation build for it
        except ValidationError as e:
            messages.error(request,e.message)
            return redirect('profile')
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.warning(request, 'Username already exists')
            return redirect('profile')
        
        if User.objects.filter(profile__phone=phone).exclude(id=user.id).exists():
            messages.warning(request,'Phone number is already already exists')
            return redirect('profile')
        if DOB:
            user.profile.DOB=DOB            
            
            # messages.warning(request,'enter Date of birth')
            # return redirect('profile') 
        user.username=username
        user.profile.phone=phone
        user.save()
        user.profile.save()
        return redirect('profile')   
        
    address=Address.objects.filter(user=user) 
    context={'user':user,
             'address':address
             } 
     
    return render(request,'address/profile.html',context)


@login_required
def change_email(request):
    if request.method == 'POST':
        otp=request.POST.get('otp')
        new_email =request.POST.get('new_email')
        resend_otp=request.POST.get('resend_otp')
        print(resend_otp)
        
        if User.objects.filter(email=new_email).exists():
            print('working')
            messages.warning(request, 'Email already exists or Associated with another account.')
            return render(request,'address/ChangeEmail.html',{'show_otp_input':False})
        
        if not otp and not resend_otp:
            send_otp(request,new_email)
            request.session['new_email']=new_email
            otp_expiry=timezone.now()+timedelta(minutes=10)
            request.session['otp_expiry']=otp_expiry.isoformat()
            messages.success(request,'OTP sent to your new eamil. Please verify within 10 minutes.')
            context={
                'show_otp_input':True,
                'new_email':new_email,
                'otp_expiry':otp_expiry
            }
            return render(request,'address/ChangeEmail.html',context)
        elif resend_otp:
            new_email=request.session.get('new_email')
            if new_email:
                send_otp(request,new_email)
                otp_expiry=timezone.now()+timedelta(minutes=10)
                request.session['otp_expiry']=otp_expiry.isoformat()
                # messages.info(request,'OTP resent to your new email. Please verify within 10 minutes.')
                return JsonResponse({
                    'success':True,
                    'message':'OTP resent to your new email. Please verify within 10 minutes.',
                    'otp_expiry':otp_expiry
                })
            else:
                # messages.error(request,'Error resending OTP. Please try again.')
                return JsonResponse({
                    'success':False,
                    'message':'Erro resending OTP. Please try again.'
                    
                })
        else:
            
            otp_secret_key =request.session.get('otp_secret_key')
            otp_valid_date =request.session.get('otp_valid_date')
            new_email = request.session.get('new_email')
            if  otp_secret_key and otp_valid_date and new_email:
                valid_date = timezone.datetime.fromisoformat(otp_valid_date)
                print(valid_date)
                if valid_date > timezone.datetime.now():
                    totp =pyotp.TOTP(otp_secret_key,interval=600)
                    if totp.verify(otp):
                        request.user.email = new_email
                        request.user.save()
                        
                        del request.session['otp_secret_key']
                        del request.session['otp_valid_date']
                        del request.session['new_email']
                        del request.session['otp_expiry']
                        
                        messages.success(request,'Email successfully changed.')
                        return redirect('profile')
                    else:
                        messages.error(request,'Invalid OTP')
                else:
                    messages.error(request,'OTP has expired.')
            else:
                messages.error(request,'Ooops...something went wrong.')
                
            context={
                'show_otp_input':True,
                'new_email':new_email,
                'otp_expiry':request.session.get('otp_expiry')
            }
            return render(request,'address/ChangeEmail.html',context)
             
            
            
            
    return render(request,'address/ChangeEmail.html',{'show_otp_input':False})


