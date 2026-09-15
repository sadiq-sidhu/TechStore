from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Coupon(models.Model):
    code        = models.CharField(max_length=50,unique=True)
    discount_amount= models.DecimalField(max_digits=10,decimal_places=2)
    min_purchase_amount=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True,
                                           help_text='Minimum puchase amount required to')
    valid_from  = models.DateTimeField()
    valid_to    = models.DateTimeField()
    is_active   = models.BooleanField(default=False)
    coupon_type = models.CharField(
        max_length=10,
        choices=[('public','Public'),('single-use','Single Use')]
    )
    def is_valide(self):
        now=timezone.now()
        return self.is_active and (self.valid_from <= now <= self.valid_to)
    def __str__(self):
        return f"{self.code} - {self.discount_amount}"
    
class CouponUsage(models.Model):
    user    = models.ForeignKey(User,on_delete=models.CASCADE)
    coupon  = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together=('user','coupon')
    def __str__(self):
        return f'{self.user.username} used {self.coupon.code} on {self.used_at}'
