from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from product.models import Product
from address.models import Address
from datetime import timedelta
from django.utils import timezone
# Create your models here.
     
class Cart(BaseModel):
    user        =models.ForeignKey(User, on_delete=models.CASCADE)
    product     =models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity    =models.PositiveIntegerField(default=1)
    
    def subtotal(self):
        return self.quantity * self.product.get_selling_price()
    
    def sub_orginal_total(self):
        return self.quantity * self.product.price
    
    def __str__(self) -> str:
        return f'{self.product}--{self.user}'
    
    
class Wishlist(BaseModel):
    user    =models.ForeignKey(User, on_delete=models.CASCADE)
    product =models.ForeignKey(Product, on_delete=models.CASCADE,related_name='product_wishlist')
    
    def __str__(self):
        return self.user

class Payment(BaseModel): 
    user            =models.ForeignKey(User, on_delete=models.CASCADE)
    amount          =models.FloatField()
    payment_method  =models.CharField(max_length=20,blank=True,null=True)
    order_id        =models.CharField(max_length=100,blank=True,null=True)
    payment_status  =models.CharField(max_length=100, blank=True,null=True)
    payment_id      =models.CharField(max_length=100,blank=True,null=True)
    paid            =models.BooleanField(default=False)
    def __str__(self) -> str:
        return f'{self.payment_status}--{self.user}'
class OrderPlaced(BaseModel):
    user        =models.ForeignKey(User, on_delete=models.CASCADE)
    address     =models.ForeignKey(Address, on_delete=models.CASCADE)
    product     =models.ManyToManyField(Product,through='OrderProduct')
    payment     =models.ForeignKey(Payment, on_delete=models.CASCADE,default="")
    
    
STATUS_CHOICES=(  
    ('pending','Pending'),
    ('packed','Packed'),
    ('on the way','On the way'),
    ('delivered','Delivered'),
    ('canceled','Canceled')
)
class OrderProduct(BaseModel):
    orders      = models.ForeignKey(OrderPlaced, on_delete=models.CASCADE)
    product     = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity    = models.PositiveIntegerField(default=1)
    order_amount= models.FloatField()
    status      = models.CharField(max_length=50,choices=STATUS_CHOICES , default='pending')
    
    def item_total(self):
        # Return 0 if the status is 'canceled', otherwise calculate the total
        if self.status.lower() == 'canceled':
            return 0
        return self.quantity * self.order_amount
    
    def is_cancellable(self):
        return timezone.now() - self.created_at <= timedelta(days=7)
