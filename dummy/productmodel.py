# models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from base.models import BaseModel

# models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from base.models import BaseModel

class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    category_slug = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to='categories', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.category_slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name_plural = 'Categories'

class Brand(BaseModel):
    brand_name = models.CharField(max_length=50)
    brand_slug = models.SlugField(unique=True, null=True, blank=True)
    brand_image = models.ImageField(upload_to='brands', null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.brand_slug = slugify(self.brand_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.brand_name

class Attribute(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    affects_image = models.BooleanField(default=False) 

    def __str__(self):
        return self.name

class AttributeValue(BaseModel):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class Product(BaseModel):
    product_name = models.CharField(max_length=150)
    product_slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='brand')
    description = models.TextField()
    attributes = models.ManyToManyField(Attribute, through='ProductAttribute')
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.product_slug = slugify(self.product_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

    @property
    def is_new(self):
        return self.created_at >= timezone.now() - timedelta(days=30)

    def get_min_price(self):
        variants = self.variants.filter(is_deleted=False)
        if variants.exists():
            return min(variant.get_selling_price() for variant in variants)
        return 0

    def get_max_price(self):
        variants = self.variants.filter(is_deleted=False)
        if variants.exists():
            return max(variant.get_selling_price() for variant in variants)
        return 0

    def get_price_range(self):
        min_price = self.get_min_price()
        max_price = self.get_max_price()
        if min_price == max_price:
            return f"₹{min_price:.2f}"
        return f"₹{min_price:.2f} - ₹{max_price:.2f}"

    def soft_delete(self):
        self.is_deleted = True
        self.variants.all().update(is_deleted=True)
        self.product_image.all().update(is_deleted=True)
        self.save()

class ProductAttribute(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_attributes')
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    values = models.ManyToManyField(AttributeValue)

    class Meta:
        unique_together = ('product', 'attribute')

    def __str__(self):
        return f"{self.product} - {self.attribute}"

class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    sku = models.CharField(max_length=100, unique=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    reorder_level = models.PositiveIntegerField(default=5)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.sku:
            if not self.uid:
                raise ValueError(f"ProductVariant for product '{self.product}' failed to get a UID after save.")
            base_sku = slugify(self.product.product_name).upper()
            short_uid = str(self.uid)[:8]
            self.sku = f"{base_sku}-{short_uid}"
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.get_variant_name()}"

    def get_variant_name(self):
        attrs = self.variant_attributes.select_related('attribute_value__attribute')
        return "/".join(
            f"{attr.attribute_value.attribute.name}: {attr.attribute_value.value}" for attr in attrs
        )

    def get_selling_price(self):
        base_price = float(self.price)
        final_price = base_price
        now = timezone.now()

        product_offers = self.product.product_offers.filter(
            is_active=True, start_date__lte=now, end_date__gte=now, discount_value__gt=0
        )
        category_offers = self.product.category.category_offers.filter(
            is_active=True, start_date__lte=now, end_date__gte=now, discount_value__gt=0
        )
        brand_offers = self.product.brand.brand_offers.filter(
            is_active=True, start_date__lte=now, end_date__gte=now, discount_value__gt=0
        )

        discounts = []
        if product_offers.exists():
            discounts.append(product_offers.first())
        if category_offers.exists():
            discounts.append(category_offers.first())
        if brand_offers.exists():
            discounts.append(brand_offers.first())

        for offer in discounts:
            if offer.discount_type == 'PERCENTAGE':
                final_price *= (1 - offer.discount_value / 100)
            else:
                final_price -= offer.discount_value

        max_allowed_price = base_price * 0.5
        if final_price < max_allowed_price:
            final_price = max_allowed_price

        min_price = base_price * 0.01
        if final_price < min_price:
            final_price = min_price

        return round(final_price, 2)

    def get_total_discount_percentage(self):
        base_price = float(self.price)
        selling_price = self.get_selling_price()
        if base_price > 0:
            return round(((base_price - selling_price) / base_price) * 100, 2)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def needs_reorder(self):
        return self.stock <= self.reorder_level

    def soft_delete(self):
        self.is_deleted = True
        self.image.all().update(is_deleted=True)
        self.save()

class VariantAttribute(BaseModel):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='variant_attributes')
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('variant', 'attribute_value')

    def __str__(self):
        return f"{self.variant} - {self.attribute_value}"

class ProductImages(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_image')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='image', null=True, blank=True)
    image = models.ImageField(upload_to='product')
    is_default = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            if self.variant:
                ProductImages.objects.filter(variant=self.variant, is_default=True).exclude(pk=self.pk).update(is_default=False)
            else:
                ProductImages.objects.filter(product=self.product, variant__isnull=True, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.variant:
            return f"{self.variant} - Image"
        return f"{self.product} - Image"

class ProductImageAttribute(BaseModel):
    image = models.ForeignKey(ProductImages, on_delete=models.CASCADE, related_name='image_attributes')
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.image} - {self.attribute_value}"