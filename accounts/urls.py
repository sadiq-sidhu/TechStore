from django.urls import path,include
from .import views

urlpatterns = [
    path('auth/',include('social_django.urls',namespace='social')),
    path('sign_up/',views.sign_up,name='sign_up'),
    path('',views.log_in,name='login'),
    path('otp/', views.otp,name='otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout',views.log_out,name='logout'),
    path('complete_profile/',views.complete_profile,name='complete_profile')
    
]
