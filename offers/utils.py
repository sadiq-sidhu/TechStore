from decimal import Decimal
from datetime import datetime
from django.core import cache 
from . models import ProductOffer,CategoryOffer

def calculate_product_pricing(product):
    cache_key = f'pricing_{product.uid}'
    pricing = cache.get(cache_key)
    price = Decimal(str(product.price))
    discounted_price = price
    best_discount= Decimal('0.00')
    
    offers = [
    ProductOffer.objects.filter(product=product, is_active=True).first(),
    CategoryOffer.objects.filter(category=product.category,is_active=True).first()     
    ]
    for offer in offers:
        if offer and offer.is_valid():
            if offer.discount_type == 'PERCENTAGE':
                best_discount=max(best_discount,Decimal(str(offer.discount_value)))
            else:
                percentage=(Decimal(str(offer.discount_value))/price)*100
                best_discount=max(best_discount,percentage)
    discounted_price=price * (1-best_discount/100)
    
    
    return{
        'price':price,
        'discounted_price': discounted_price,
        'total_discount_percentage' : round(best_discount,2),
        'has_offer':best_discount > 0,
    }
        
        