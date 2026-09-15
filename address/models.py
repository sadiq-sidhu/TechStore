from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from accounts.models import profile
# Create your models here.
STATE_CHOICES={
    ('Andhra Pradesh', 'Andhra Pradesh'),
    ('Arunachal Pradesh', 'Arunachal Pradesh'),
    ('Assam', 'Assam'),
    ('Bihar', 'Bihar'),
    ('Chhattisgarh', 'Chhattisgarh'),
    ('Goa', 'Goa'),
    ('Gujarat', 'Gujarat'),
    ('Haryana', 'Haryana'),
    ('Himachal Pradesh', 'Himachal Pradesh'),
    ('Jharkhand', 'Jharkhand'),
    ('Karnataka', 'Karnataka'),
    ('Kerala', 'Kerala'),
    ('Maharashtra', 'Maharashtra'),
    ('Madhya Pradesh', 'Madhya Pradesh'),
    ('Manipur', 'Manipur'),
    ('Meghalaya', 'Meghalaya'),
    
}


class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=255, choices=[('home', 'Home'), ('office', 'Office'),('other','Other')])
    name=models.CharField(max_length=220,)
    locality = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    state=models.CharField(choices=STATE_CHOICES,max_length=100)
    mobile=models.BigIntegerField()

    def __str__(self):
        return f"{self.user.username}'s {self.type} Address"