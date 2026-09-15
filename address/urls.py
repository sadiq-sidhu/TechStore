from django.urls import path
from .import views
from .forms import MyPasswordChangeForm
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('profile/add_address',views.AddAddress.as_view(),name='profile_add_address'),
    path('update<str:pk>',views.UpdateAddress.as_view(),name='update_address'),
    path('delete<str:pk>',views.Delete,name='delete_address'),
    path('viewaddress',views.ViewAddress,name='view_address'),
    path('home',views.profile,name='profile'),
    path('changeemail',views.change_email,name='change_email'),
    
    path('passwordchange',auth_view.PasswordChangeView.as_view(template_name='address/ChangePassword.html', form_class=MyPasswordChangeForm, success_url='/address/passwordchangedone'),name='change_password'),
    path('passwordchangedone', auth_view.PasswordChangeDoneView.as_view(template_name='address/PasswordDone.html'), name='passwordchangedone'),
]