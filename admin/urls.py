from django.urls import path
from .import views

urlpatterns = [
    path('ad/',views.dashboard,name='dashboard'),
    
    path('user_list',views.user_list,name='user_list'),
    path('block_user/<str:pk>',views.block_user,name='block_user'),
    path('adminLogin',views.admin_login, name='admin_login'),
    path('ad_log_out',views.ad_log_out,name='ad_log_out'),
    
    path('product_list',views.product_list,name='product_list'),    
    path('add_product',views.add_product, name='add_product'),  
    path('delete_product/<str:pk>',views.delete_product,name='delete_product'),
    
    path('categories',views.categories,name='categories'),
    path('add_category',views.add_category,name='add_category'),
    path('delete_categories/<str:pk>',views.delete_categories,name='delete_categories'),
    path('edit_categories/<str:pk>',views.edit_categories,name='edit_categories'),
    
]
