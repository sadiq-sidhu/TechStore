from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel

# Create your models here.
class Wallet(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance= models.DecimalField(max_digits=7,decimal_places=2,default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Walltet"
class WalletTransaction(BaseModel):
    TRANSACTION_TYPE_CHOICES=[
        ('CREDIT','Credit'),
        ('DEBIT','Debit'),
        ('REFUND','Refund'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=7,decimal_places=2)
    description=models.TextField(blank=True)
    payment_id=models.CharField(max_length=100,blank=True,null=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} on {self.created_at}"
    