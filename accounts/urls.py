from django.urls import path
from .import views

urlpatterns = [
    path('sign_up/',views.sign_up,name='sign_up'),
    path('',views.log_in,name='login'),
    path('otp/', views.otp,name='otp'),
    path('logout',views.log_out,name='logout')
]
