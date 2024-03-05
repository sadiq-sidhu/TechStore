from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel

# Create your models here.

class profile(BaseModel):
    user= models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile" )
    is_verified =models.BooleanField(default=False)
    profile_image=models.ImageField(upload_to='profile', blank=True, null=True)
    phone=models.IntegerField()
    DOB=models.DateField()
    
    def __str__(self):
        return self.user.username
    