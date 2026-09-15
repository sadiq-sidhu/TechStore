from django import template
from offers.utils import calculate_product_pricing

register=template.Library()

def get_product_pricing(product,key):
    pricing = calculate_product_pricing(product)
    return pricing.get(key,0)