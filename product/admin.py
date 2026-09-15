from django.contrib import admin
from .models import (
    Category, Brand, Attribute, AttributeValue, Product, ProductVariant,
    ProductAttribute, VariantAttribute, ProductImages, ProductImageAttribute
)

# Inline for ProductImage within Product
class ProductImageInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ('image', 'is_default', 'display_order', 'is_deleted')
    readonly_fields = ('uid',)

# Inline for VariantAttribute within ProductVariant
class VariantAttributeInline(admin.TabularInline):
    model = VariantAttribute
    extra = 1
    fields = ('attribute_value', 'is_deleted')
    autocomplete_fields = ['attribute_value']

# Inline for ProductVariant within Product
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('price', 'stock', 'sku', 'is_default', 'is_deleted', 'reorder_level')
    readonly_fields = ('sku',)

# Inline for ProductAttribute within Product
class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1
    autocomplete_fields = ['attribute']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_slug', 'is_deleted')
    search_fields = ('category_name',)
    prepopulated_fields = {'category_slug': ('category_name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'brand_slug', 'is_deleted')
    search_fields = ('brand_name',)
    prepopulated_fields = {'brand_slug': ('brand_name',)}

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'affects_image', 'is_deleted')
    search_fields = ('name',)

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'is_deleted')
    search_fields = ('value',)
    list_filter = ('attribute',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'brand', 'is_new', 'is_deleted')
    search_fields = ('product_name',)
    list_filter = ('category', 'brand')
    prepopulated_fields = {'product_slug': ('product_name',)}
    inlines = [ProductAttributeInline, ProductVariantInline, ProductImageInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'price', 'stock', 'sku', 'is_default', 'is_in_stock', 'needs_reorder', 'is_deleted')
    search_fields = ('sku', 'product__product_name')
    list_filter = ('is_default', 'is_deleted')
    inlines = [VariantAttributeInline]

@admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ('product', 'variant', 'is_default', 'display_order', 'is_deleted')
    list_filter = ('is_default', 'is_deleted')
    search_fields = ('product__product_name', 'variant__sku')

@admin.register(ProductImageAttribute)
class ProductImageAttributeAdmin(admin.ModelAdmin):
    list_display = ('image', 'attribute_value', 'is_deleted')
    list_filter = ('attribute_value__attribute',)

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'is_deleted')
    list_filter = ('attribute',)

@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ('variant', 'attribute_value', 'is_deleted')
    list_filter = ('attribute_value__attribute',)