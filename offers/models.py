from django.utils import timezone
from django.db import models
from base.models import BaseModel
from product.models import Product,Category,Brand
from django.core.exceptions import ValidationError
# Create your models here.
OFFER_TYPE_CHOICES=(
    ('PERCENTAGE','Percentage'),
    ('FIXED','Fixed Amount')
)
class ProductOffer(BaseModel):
    product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name='product_offers')
    discount_type=models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    discount_value=models.FloatField()
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()
    is_active=models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.product.product_name}-{self.discount_value} {self.discount_type}"
    def is_valid(self):
        now = timezone.now()
        return (self.is_active and self.start_date <= now <= self.end_date and self.discount_value > 0)
    
    def clean(self):
        if self.discount_value < 0:
            raise ValidationError({"discount_value": "Discount value cannot be negative."})
        if self.start_date >= self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})
        if not hasattr(self, 'product') or not self.product:
            return
        base_price = float(self.product.price)
        final_price = base_price
        if self.discount_type == 'PERCENTAGE':
            final_price *= (1 - self.discount_value / 100)
        else:
            final_price -= self.discount_value
        category_offers = self.product.category.category_offers.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
            discount_value__gt=0
        )
        brand_offers = self.product.brand.brand_offers.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
            discount_value__gt=0
        )
        if category_offers.exists():
            offer = category_offers.first()
            if offer.discount_type == 'PERCENTAGE':
                final_price *= (1 - offer.discount_value / 100)
            else:
                final_price -= offer.discount_value
        if brand_offers.exists():
            offer = brand_offers.first()
            if offer.discount_type == 'PERCENTAGE':
                final_price *= (1 - offer.discount_value / 100)
            else:
                final_price -= offer.discount_value
        total_discount = ((base_price - final_price) / base_price) * 100
        if total_discount > 50:
            raise ValidationError(
                f"Total discount of {total_discount:.2f}% exceeds the maximum allowed 50%."
            )
        min_price = base_price * 0.01
        if final_price < min_price:
            raise ValidationError(
                "This discount would reduce the price below the minimum threshold (1% of base price)."
            )
    
class CategoryOffer(BaseModel):
    category=models.ForeignKey(Category, on_delete=models.CASCADE,related_name='category_offers')
    discount_type=models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    discount_value=models.FloatField()
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()
    is_active=models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.category.category_name} - {self.discount_value} {self.discount_type}"
    def is_valid(self):
        now=timezone.now()
        return (self.is_active and self.start_date <= now <= self.end_date and self.discount_value > 0)
    def clean(self):
        if self.discount_value < 0:
            raise ValidationError({"discount_value": "Discount value cannot be negative."})
        if self.start_date >= self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})
        if not hasattr(self, 'category') or not self.category:
            return
        products = Product.objects.filter(category=self.category, is_deleted=False)
        for product in products:
            base_price = float(product.price)
            final_price = base_price
            product_offers = product.product_offers.filter(
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
                discount_value__gt=0
            )
            if product_offers.exists():
                offer = product_offers.first()
                if offer.discount_type == 'PERCENTAGE':
                    final_price *= (1 - offer.discount_value / 100)
                else:
                    final_price -= offer.discount_value
            if self.discount_type == 'PERCENTAGE':
                final_price *= (1 - self.discount_value / 100)
            else:
                final_price -= self.discount_value
            brand_offers = product.brand.brand_offers.filter(
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
                discount_value__gt=0
            )
            if brand_offers.exists():
                offer = brand_offers.first()
                if offer.discount_type == 'PERCENTAGE':
                    final_price *= (1 - offer.discount_value / 100)
                else:
                    final_price -= offer.discount_value
            total_discount = ((base_price - final_price) / base_price) * 100
            if total_discount > 50:
                raise ValidationError(
                    f"Total discount of {total_discount:.2f}% for product {product.product_name} "
                    "exceeds the maximum allowed 50%."
                )
            min_price = base_price * 0.01
            if final_price < min_price:
                raise ValidationError(
                    f"This discount would reduce the price of {product.product_name} below the "
                    "minimum threshold (1% of base price)."
                )

class BrandOffer(BaseModel):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='brand_offers')
    discount_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)
    discount_value = models.FloatField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand.brand_name} - {self.discount_value} {self.discount_type}"

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date and
            self.discount_value > 0
        )

    def clean(self):
        if self.discount_value < 0:
            raise ValidationError({"discount_value": "Discount value cannot be negative."})
        if self.start_date >= self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})
        if not hasattr(self, 'brand') or not self.brand:
            return
        products = Product.objects.filter(brand=self.brand, is_deleted=False)
        for product in products:
            base_price = float(product.price)
            final_price = base_price
            product_offers = product.product_offers.filter(
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
                discount_value__gt=0
            )
            if product_offers.exists():
                offer = product_offers.first()
                if offer.discount_type == 'PERCENTAGE':
                    final_price *= (1 - offer.discount_value / 100)
                else:
                    final_price -= offer.discount_value
            category_offers = product.category.category_offers.filter(
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
                discount_value__gt=0
            )
            if category_offers.exists():
                offer = category_offers.first()
                if offer.discount_type == 'PERCENTAGE':
                    final_price *= (1 - offer.discount_value / 100)
                else:
                    final_price -= offer.discount_value
            if self.discount_type == 'PERCENTAGE':
                final_price *= (1 - self.discount_value / 100)
            else:
                final_price -= self.discount_value
            total_discount = ((base_price - final_price) / base_price) * 100
            if total_discount > 50:
                raise ValidationError(
                    f"Total discount of {total_discount:.2f}% for product {product.product_name} "
                    "exceeds the maximum allowed 50%."
                )
            min_price = base_price * 0.01
            if final_price < min_price:
                raise ValidationError(
                    f"This discount would reduce the price of {product.product_name} below the "
                    "minimum threshold (1% of base price)."
                )