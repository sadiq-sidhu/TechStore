from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from product.models import Product

# Create your models here.
class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user
    
    
class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_active=models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.product