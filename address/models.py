from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
# Create your models here.
class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_type = models.CharField(max_length=255, choices=[('home', 'Home'), ('office', 'Office')])
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.username}'s {self.address_type} Address"