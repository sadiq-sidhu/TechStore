from django.shortcuts import get_object_or_404,redirect
from .models import profile
from datetime import date

def save_profile(backend,user,response,*args, **kwargs):
    print(f'user:{user} backend name {backend.name}')
    if backend.name=='google-oauth2':
        print('working here')
        
        user_profile,created= profile.objects.get_or_create(
            user=user,
            defaults={'phone':None,
                      'DOB':None,
                      'is_verified':True}
            )
        print(f'profile created:{created}, is_verified:{user_profile.is_verified}')
        
        if not user_profile.is_verified:
            user_profile.is_verified=True 
            user_profile.save()    
            
        if user_profile.phone is None or user_profile.DOB is None:
            kwargs['request'].session['needs_profile_completion']=True
            kwargs['request'].session['google_auth_user']=True
        else:
            if 'needs_profile_completion' in kwargs['request'].session:
                del kwargs['request'].session['needs_profile_completion']
            if 'google_auth_user' in kwargs['request'].session:
                del kwargs['request'].session['google_auth_user']
        if response.get('picture') and not user_profile.profile_image:
            pass
        
                