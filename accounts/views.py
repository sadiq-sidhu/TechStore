from datetime import date, datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
import pyotp
from .forms import Myform
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from .otp import send_otp
from .models import profile
import logging
from django.views.decorators.http import require_POST

logger=logging.getLogger(__name__)

# Create your views here.

def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        dob = request.POST['DOB']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        form = Myform(request.POST)
        
        logger.debug(f"Sign-up POST: username={username}, email={email}, phone={phone}, DOB={dob}")
        
        if password1 != password2:
            messages.error(request, 'Password and Confirm Password do not match')
            logger.debug("Password mismatch")
            return redirect('sign_up')
        
        if User.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists')
            logger.debug("Username exists")
            return redirect('sign_up')
        
        if User.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists')
            logger.debug("Email exists")
            return redirect('sign_up')
        
        if profile.objects.filter(phone=phone).exists():
            messages.warning(request, 'Phone number already exists')
            logger.debug("Phone exists")
            return redirect('sign_up')
        
        if not form.is_valid():
            messages.error(request, 'Captcha error')
            logger.debug("Captcha error")
            return redirect('sign_up')
        
        try:
            phone = phone.strip()
            if not phone.isdigit() or len(phone) != 10 or phone == '0000000000':
                messages.error(request, 'Phone number must be exactly 10 digits and not all zeros')
                logger.debug("Invalid phone number")
                return redirect('sign_up')
            
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            if dob_date >= datetime.now().date():
                messages.error(request, 'Date of Birth cannot be today or in the future')
                logger.debug("Invalid DOB")
                return redirect('sign_up')
            
            user = User.objects.create_user(username=username, email=email, password=password1)
            user_profile = profile(user=user, phone=int(phone), DOB=dob_date)
            user.save()
            user_profile.save()
            
            request.session['username'] = username
            request.session['signup_email'] = email
            send_otp(request, email)
            logger.debug(f"User {username} created, OTP sent")
            return redirect('otp')
        
        except ValueError as e:
            messages.error(request, f'Invalid input: {e}')
            logger.error(f"Sign-up error: {e}")
            return redirect('sign_up')
        except Exception as e:
            messages.error(request, f'Error creating account: {e}')
            logger.error(f"Sign-up error: {e}")
            return redirect('sign_up')
    
    form = Myform()
    return render(request, 'accounts/sign_up.html', {'form': form})

def otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        username = request.session.get('username')
        otp_secret_key = request.session.get('otp_secret_key')
        otp_valid_date = request.session.get('otp_valid_date')
        
        logger.debug(f"OTP verification attempt: username={username}, otp={otp}")
        
        if not username or not otp_secret_key or not otp_valid_date:
            logger.debug("Missing session data")
            return JsonResponse({'status': 'error', 'message': 'Session expired or invalid. Please sign up again.'}, status=400)
        
        try:
            valid_date = datetime.fromisoformat(otp_valid_date)
            if valid_date > datetime.now():
                totp = pyotp.TOTP(otp_secret_key, interval=180)
                if totp.verify(otp):
                    user = get_object_or_404(User, username=username)
                    user.profile.is_verified = True
                    user.profile.save()
                    logger.debug(f"User {username} OTP verified, profile updated")
                    
                    # Clear session
                    for key in ['username', 'otp_secret_key', 'otp_valid_date', 'signup_email', 'otp_resend_allowed']:
                        if key in request.session:
                            del request.session[key]
                    
                    return JsonResponse({'status': 'success', 'message': 'OTP verified successfully!', 'redirect': '/'})
                else:
                    logger.debug("Invalid OTP")
                    return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})
            else:
                logger.debug("OTP expired")
                return JsonResponse({'status': 'error', 'message': 'OTP has expired'})
        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred during OTP verification'}, status=500)
    
    return render(request, 'accounts/otp.html', {'email': request.session.get('signup_email')})

@require_POST
def resend_otp(request):
    email = request.session.get('signup_email')
    otp_resend_allowed = request.session.get('otp_resend_allowed')
    
    if not email or 'username' not in request.session:
        logger.debug("Resend OTP failed: no email or username in session")
        return JsonResponse({'status': 'error', 'message': 'Session expired. Please sign up again.'}, status=400)
    
    try:
        resend_allowed_date = datetime.fromisoformat(otp_resend_allowed)
        if datetime.now() < resend_allowed_date:
            time_remaining = int((resend_allowed_date - datetime.now()).total_seconds())
            logger.debug(f"Resend OTP blocked: {time_remaining} seconds remaining")
            return JsonResponse({'status': 'error', 'message': f'Please wait {time_remaining} seconds before resending OTP'}, status=429)
        
        send_otp(request, email)
        logger.debug(f"Resend OTP successful for {email}")
        return JsonResponse({'status': 'success', 'message': 'New OTP sent successfully'})
    
    except Exception as e:
        logger.error(f"Resend OTP error: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to resend OTP'}, status=500)       

def log_in(request):
    # Redirect authenticated users
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and (request.user.profile.phone is None or request.user.profile.DOB is None):
            request.session['needs_profile_completion'] = True
            request.session['google_auth_user'] = True
            logger.debug(f"Authenticated user {request.user.username} has incomplete profile, redirecting to complete_profile")
            return redirect('complete_profile')
        logger.debug(f"Authenticated user {request.user.username} redirecting to home")
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        logger.debug(f"Login attempt for username: {username}")

        user_obj = User.objects.filter(username=username)
        if not user_obj.exists():
            messages.warning(request, 'Account not found')
            logger.debug("Username does not exist")
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            messages.error(request, 'Invalid password')
            logger.debug("Invalid password")
            return redirect('login')
        
        if not user.is_active:
            messages.error(request, 'Your account is blocked')
            logger.debug("User is blocked")
            return redirect('login')
        
        if hasattr(user, 'social_auth') and user.social_auth.filter(provider='google-oauth2').exists():
            if user.profile.phone is None or user.profile.DOB is None:
                request.session['needs_profile_completion'] = True
                request.session['google_auth_user'] = True
                logger.debug("Google user has incomplete profile")
        
        if not user.profile.is_verified and not user.social_auth.filter(provider='google-oauth2').exists():
            messages.warning(request, 'Your account is not OTP verified')
            logger.debug("Non-Google user not OTP verified")
            return redirect('login')
        
        login(request, user)
        logger.debug(f"User {username} logged in successfully")
        
        if request.session.get('needs_profile_completion'):
            return redirect('complete_profile')
        return redirect('home')
    
    return render(request, 'accounts/login.html')

def log_out(request):
    request.session.flush()
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    logout(request)
    response= redirect('login')
    response.delete_cookie('sessionid')
    return response

@login_required
def complete_profile(request):
    if not request.session.get('needs_profile_completion') or not request.session.get('google_auth_user'):
        logger.debug(f"User {request.user.username} attempted to access complete_profile without proper session flags")
        messages.warning(request, 'Please log in through Google to complete your profile')
        return redirect('login')
    
    user_profile = request.user.profile
    
    if user_profile.phone is not None and user_profile.DOB is not None:
        logger.debug(f"Profile already complete for user {request.user.username}")
        for key in ['needs_profile_completion', 'google_auth_user', 'social_auth_user_id', 'social_auth_email']:
            if key in request.session:
                del request.session[key]
        return redirect('home')
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        dob = request.POST.get('DOB')
        logger.debug(f"complete_profile POST: phone={phone}, DOB={dob}")
        
        if not phone or not dob:
            messages.error(request, 'Phone and Date of Birth are required')
            logger.debug("Missing phone or DOB")
            return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})
        
        try:
            phone = phone.strip()
            if not phone.isdigit():
                messages.error(request, 'Phone number must contain only digits')
                logger.debug("Invalid phone: non-digit characters")
                return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})
            
            phone_int = int(phone)
            if len(phone) != 10:
                messages.error(request, 'Phone number must be exactly 10 digits')
                logger.debug(f"Invalid phone length: {len(phone)} digits")
                return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})
            
            if phone == '0000000000':
                messages.error(request, 'Invalid phone number')
                logger.debug("Invalid phone: all zeros")
                return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})
            
            if profile.objects.filter(phone=phone_int).exclude(user=request.user).exists():
                messages.error(request, 'Phone number is already in use by another account')
                logger.debug(f"Phone number {phone} already exists")
                return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})
            
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            if dob_date >= date.today():
                messages.error(request, 'Date of Birth cannot be today or in the future')
                logger.debug(f"Invalid DOB: {dob_date} is today or future")
                return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})
            
            user_profile.phone = phone_int
            user_profile.DOB = dob_date
            user_profile.is_verified = True  
            user_profile.save()
            logger.debug(f"Profile saved: phone={user_profile.phone}, DOB={user_profile.DOB}")
            
            for key in ['needs_profile_completion', 'google_auth_user', 'social_auth_user_id', 'social_auth_email']:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, 'Profile completed successfully!')
            logger.debug(f"User {request.user.username} completed profile")
            return redirect('home')
        
        except ValueError as e:
            messages.error(request, 'Invalid phone number or date format')
            logger.error(f"Validation error: {e}")
            return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})
        except Exception as e:
            messages.error(request, f'Error saving profile: {e}')
            logger.error(f"Unexpected error: {e}")
            return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})
    
    return render(request, 'accounts/complete_profile.html', {'email': request.user.email, 'today': date.today()})