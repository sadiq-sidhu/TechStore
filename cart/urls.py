from django.urls import path
from .import views


urlpatterns = [
    # cart
    path('cart/',views.cart,name='cart'),
    path('add_cart/',views.add_cart,name='add_cart'),
    path('pluscart/',views.pluscart,name='pluscart'),
    path('minuscart/',views.minuscart,name='minuscart'),
    path('removecart/',views.removecart,name='removecart'),
    
    # whishlist
    path('wishlist/',views.wishlist,name='wishlist'),
    path('pluswishlist/',views.plus_wishlist,name='pluswishlist'),
    path('minuswishlist/',views.minus_wishlist,name='minuswishlist'),
    
    # checkout
    # path('checkout/',views.checkout.as_view(),name='checkout'),
    # path('save_address/',views.save_address, name='save_address'),
    # path('paymentdone/',views.payment_done,name='paymentdone'), 
    path('checkout_page/',views.checkout_page,name='checkout_page'),
    path('add_address/',views.add_address,name='add_address'),
    path('order_list/', views.order_list, name='order_list'),
    path('order_cancel/<str:pk>',views.order_cancel,name='order_cancel'),
    
    path('payment/callback/', views.payment_callback, name='payment__callback'),
    
    #coupon managment
    path('apply_coupon/',views.apply_coupon,name='apply_coupon'),
    path('remove_coupon',views.remove_coupon,name='remove_coupon')
    
    
]