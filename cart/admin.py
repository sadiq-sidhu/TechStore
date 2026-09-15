from django.contrib import admin
from .models import Cart,Payment,Wishlist,OrderPlaced,OrderProduct
# Register your models here.
admin.site.register(Cart)
admin.site.register(Payment)
admin.site.register(OrderPlaced)
admin.site.register(Wishlist)
admin.site.register(OrderProduct)