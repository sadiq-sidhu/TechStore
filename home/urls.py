from django.urls import path
from .import views

urlpatterns = [

    path('home/',views.home,name='home'),
    # path('category/<slug:val>/',views.CategoryView.as_view(),name='category'),
    path('category/<slug:val>/',views.category_view, name='category'),
    path('product/<slug:slug>/', views.get_product, name='get_product'),
    path('search_product',views.search_product,name='search_product'),
    
    path('dprofile',views.profile,name='d_profile')
    
]