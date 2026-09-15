from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel

class profile(BaseModel):
    user= models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile" )
    is_verified =models.BooleanField(default=False)
    profile_image=models.ImageField(upload_to='profile', blank=True, null=True)
    phone=models.BigIntegerField(null=True,blank=True)
    DOB=models.DateField(null=True,blank=True)
    
    def __str__(self):
        return self.user.username
    class Meta:
        db_table='accounts_profile'
    