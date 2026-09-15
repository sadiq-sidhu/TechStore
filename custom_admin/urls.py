from django.urls import path
from .import views

urlpatterns = [
    path('ad/',views.dashboard,name='dashboard'),
    #admin login and logout
    path('adminLogin',views.admin_login, name='admin_login'),
    path('ad_log_out',views.ad_log_out,name='ad_log_out'),
    
    path('user_list',views.user_list,name='user_list'),
    path('block_user/<str:pk>',views.block_user,name='block_user'),
    path('user_details/<str:pk>',views.user_details,name='user_details'),
 
    path('categories',views.categories,name='categories'),
    path('add_category',views.add_category,name='add_category'),
    path('delete_categories/<str:pk>',views.delete_categories,name='delete_categories'),
    path('edit_categories/<str:pk>',views.edit_categories,name='edit_categories'),
    
    path('orders',views.orders,name='orders'),
    path('order_details/<str:pk>',views.order_details,name='order_details'),
    path('order_change/<str:order_uid>', views.change_order_status, name='change_order_status'),
    
    path('coupon/',views.coupon_list,name='coupon_list'),
    path('coupon/add/',views.add_coupon,name='add_coupon'),
    path('coupon/edit/<int:coupon_id>',views.edit_coupon,name='edit_coupon'),
    path('coupon/delete/<int:coupon_id>',views.delete_coupon,name='delete_coupon'),
    
    
    path('offers/', views.offer_list, name='offer_list'),
    path('add_product_offer/', views.add_product_offer, name='add_product_offer'),
    path('add_category_offer/', views.add_category_offer, name='add_category_offer'),
    path('add_brand_offer/', views.add_brand_offer, name='add_brand_offer'),
    
    path('edit_product_offer/<uuid:pk>/', views.edit_product_offer, name='edit_product_offer'),
    path('edit_category_offer/<uuid:pk>/', views.edit_category_offer, name='edit_category_offer'),
    path('edit_brand_offer/<uuid:pk>/', views.edit_brand_offer, name='edit_brand_offer'),
    
    path('delete_product_offer/<uuid:pk>/', views.delete_product_offer, name='delete_product_offer'),
    path('delete_category_offer/<uuid:pk>/', views.delete_category_offer, name='delete_category_offer'),
    path('delete_brand_offer/<uuid:pk>/', views.delete_brand_offer, name='delete_brand_offer'),
    
    # path('product_list',views.product_list,name='product_list'),    
    # path('add_product',views.add_product, name='add_product'),  
    # path('edit_product/<str:pk>',views.edit_product,name='edit_product'),
    # path('delete_product/<str:pk>',views.delete_product,name='delete_product'),
    
    # path('products_list/', views.product_list, name='product_list'),
    # path('product/add/', views.product_add, name='product_add'),
    # path('product/edit/<uuid:product_id>/', views.product_edit, name='product_edit'),
    # path('product/delete/<uuid:product_id>/', views.product_delete, name='product_delete'),
    # path('variant/add/<uuid:product_id>/', views.variant_add, name='variant_add'),
    # path('variant/delete/<uuid:variant_id>/', views.variant_delete, name='variant_delete'),
    # path('image/add/<uuid:product_id>/', views.image_add, name='image_add'),
    # path('image/delete/<uuid:image_id>/', views.image_delete, name='image_delete'),
    
    path('attributes/', views.attribute_list, name='attribute_list'),
    path('attribute/add/', views.attribute_add, name='attribute_add'),
    path('attribute/edit/<uuid:attribute_id>/', views.attribute_edit, name='attribute_edit'),
    path('attribute/value/add/<uuid:attribute_id>/', views.attribute_value_add, name='attribute_value_add'),
    path('attribute/value/edit/<uuid:attribute_value_id>/', views.attribute_value_edit, name='attribute_value_edit'),
    
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<uuid:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<uuid:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/<uuid:product_id>/variants/', views.product_manage_variants, name='product_manage_variants'),
    
    path('variants/<uuid:variant_id>/edit/', views.variant_edit, name='variant_edit'),
    path('variants/<uuid:variant_id>/delete/', views.variant_delete, name='variant_delete'),

    # path('variants/<uuid:variant_id>/images/', views.variant_image_manage, name='variant_image_manage'),
    # path('variants/<uuid:variant_id>/images/add/', views.variant_image_add, name='variant_image_add'),
    # path('images/<uuid:image_id>/delete/', views.variant_image_delete, name='variant_image_delete'),
    path('products/<uuid:product_id>/variants/groups/<int:group_hash>/images/',views.variant_group_images,name='variant_group_images'),   
 
]