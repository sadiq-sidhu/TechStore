from django.urls import path
from . import views

urlpatterns = [
    path('wallet',views.wallet_view,name='wallet_view'),
    path('wallet/add-money/',views.add_money,name='add_money'),
    path('wallet/payment-callback',views.payment_callback,name='payment_callback'),
]
