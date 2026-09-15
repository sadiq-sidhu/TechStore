from django import forms
from coupon.models import Coupon
from offers.models import BrandOffer, CategoryOffer, ProductOffer
from django.core.exceptions import ValidationError
from django.utils import timezone
from product.models import Attribute, AttributeValue, Product, ProductImageAttribute, ProductImages, ProductVariant, VariantAttribute
from django.core.files.base import ContentFile
import base64
from io import BytesIO
from PIL import Image
from django.forms import inlineformset_factory

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code','discount_amount','min_purchase_amount','valid_from', 'valid_to', 'is_active','coupon_type']
        widgets = {
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter coupon code'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discount amount'
            }),
            'min_purchase_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter minimum purchase amount'
            }),
            'valid_from': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'valid_to': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'coupon_type': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    def clean(self):
        cleaned_data=super().clean()
        valid_from = cleaned_data.get('valid_from')
        valid_to = cleaned_data.get('valid_to')
        
        if valid_from and valid_to and valid_from >= valid_to:
            raise forms.ValidationError('The start date must be before the end date.')
        
        return cleaned_data


class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['product', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount value'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        discount_value = cleaned_data.get('discount_value')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        product = cleaned_data.get('product')

        if discount_value is not None and discount_value < 0:
            raise ValidationError({"discount_value": "Discount value cannot be negative."})

        if start_date and end_date and start_date >= end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        if product:
            base_price = float(product.price)
            final_price = base_price
            discount_type = cleaned_data.get('discount_type')

            # Apply this offer
            if discount_type == 'PERCENTAGE':
                final_price *= (1 - discount_value / 100)
            else:
                final_price -= discount_value

            # Check existing offers
            now = timezone.now()
            category_offers = product.category.category_offers.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now,
                discount_value__gt=0
            )
            brand_offers = product.brand.brand_offers.filter(
                is_active=True,
                start_date__lte=now,
                end_date__gte=now,
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
            if total_discount >= 40:
                self.add_error(None, f"Warning: Total discount is {total_discount:.2f}%, which is high.")

class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['category', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount value'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        discount_value = cleaned_data.get('discount_value')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        category = cleaned_data.get('category')

        if discount_value is not None and discount_value < 0:
            raise ValidationError({"discount_value": "Discount value cannot be negative."})

        if start_date and end_date and start_date >= end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        if category:
            products = Product.objects.filter(category=category, is_deleted=False)
            for product in products:
                base_price = float(product.price)
                final_price = base_price
                discount_type = cleaned_data.get('discount_type')

                # Apply existing product offer
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

                # Apply this category offer
                if discount_type == 'PERCENTAGE':
                    final_price *= (1 - discount_value / 100)
                else:
                    final_price -= discount_value

                # Apply existing brand offer
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
                        f"Total discount of {total_discount:.2f}% for product {product.product_name} exceeds the maximum allowed 50%."
                    )
                min_price = base_price * 0.01
                if final_price < min_price:
                    raise ValidationError(
                        f"This discount would reduce the price of {product.product_name} below the minimum threshold (1% of base price)."
                    )
                # if total_discount >= 40:
                #     self.add_error(None, f"Warning: Total discount for {product.product_name} is {total_discount:.2f}%, which is high.")

class BrandOfferForm(forms.ModelForm):
    class Meta:
        model = BrandOffer
        fields = ['brand', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'discount_type': forms.Select(attrs={'class': 'form-select'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter discount value'}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        discount_value = cleaned_data.get('discount_value')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        brand = cleaned_data.get('brand')

        if discount_value is not None and discount_value < 0:
            raise ValidationError({"discount_value": "Discount value cannot be negative."})

        if start_date and end_date and start_date >= end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        if brand:
            products = Product.objects.filter(brand=brand, is_deleted=False)
            for product in products:
                base_price = float(product.price)
                final_price = base_price
                discount_type = cleaned_data.get('discount_type')

                # Apply existing product offer
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

                # Apply existing category offer
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

                # Apply this brand offer
                if discount_type == 'PERCENTAGE':
                    final_price *= (1 - discount_value / 100)
                else:
                    final_price -= discount_value

                total_discount = ((base_price - final_price) / base_price) * 100
                if total_discount > 50:
                    raise ValidationError(
                        f"Total discount of {total_discount:.2f}% for product {product.product_name} exceeds the maximum allowed 50%."
                    )
                min_price = base_price * 0.01
                if final_price < min_price:
                    raise ValidationError(
                        f"This discount would reduce the price of {product.product_name} below the minimum threshold (1% of base price)."
                    )
                if total_discount >= 40:
                    self.add_error(None, f"Warning: Total discount for {product.product_name} is {total_discount:.2f}%, which is high.")
                    

######################################


class ProductForm(forms.ModelForm):
    applicable_attributes = forms.ModelMultipleChoiceField(
        queryset=Attribute.objects.filter(is_deleted=False),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select attributes that apply to this product"
    )
    
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'brand', 'description']
        
class VariantCreationForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['price', 'stock', 'is_default', 'reorder_level']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        super().__init__(*args, **kwargs)
        
        # Add fields for each applicable attribute
        for attribute in self.product.attributes.all():
            self.fields[f'attr_{attribute.uid}'] = forms.ModelChoiceField(
                queryset=attribute.values.filter(is_deleted=False),
                label=attribute.name,
                required=True,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

class VariantEditForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['price', 'stock', 'is_default', 'reorder_level']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImages
        fields = ['image', 'is_default', 'display_order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.variant = kwargs.pop('variant', None)
        super().__init__(*args, **kwargs)
        
        if self.instance.pk and self.variant:
            image_attrs = VariantAttribute.objects.filter(
                variant=self.variant,
                attribute_value__attribute__affects_image=True,
                is_deleted=False
            ).select_related('attribute_value', 'attribute_value__attribute')
            
            for attr in image_attrs:
                field_name = f'attr_{attr.uid}'
                self.fields[field_name] = forms.BooleanField(
                    label=f"{attr.attribute_value.attribute.name}: {attr.attribute_value.value}",
                    required=False,
                    initial=True,
                    widget=forms.CheckboxInput(attrs={
                        'class': 'form-check-input attribute-checkbox',
                        'data-attribute': attr.attribute_value.attribute.name
                    }))
                
                exists = self.instance.image_attributes.filter(
                    attribute_value=attr.attribute_value
                ).exists()
                self.fields[field_name].initial = exists

    def save(self, commit=True):
        image = super().save(commit=False)
        if commit:
            image.save()
            self.save_m2m()
            if self.variant:
                for field_name, value in self.cleaned_data.items():
                    if field_name.startswith('attr_') and value:
                        attr_uid = field_name.split('_')[1]
                        try:
                            attr = VariantAttribute.objects.get(uid=attr_uid, variant=self.variant)
                            ProductImageAttribute.objects.get_or_create(
                                image=image,
                                attribute_value=attr.attribute_value
                            )
                        except VariantAttribute.DoesNotExist:
                            pass
        return image
    
class VariantAttributeForm(forms.Form):
    attribute = forms.ModelChoiceField(
        queryset=Attribute.objects.filter(is_deleted=False),
        widget=forms.Select(attrs={'class': 'form-control select2 attribute-select'})
    )
    attribute_values = forms.ModelMultipleChoiceField(
        queryset=AttributeValue.objects.none(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'attribute' in self.data:
            try:
                attribute_id = self.data.get('attribute')
                self.fields['attribute_values'].queryset = AttributeValue.objects.filter(
                    attribute__uid=attribute_id, is_deleted=False
                )
            except (ValueError, TypeError):
                pass

class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = ['name', 'affects_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter attribute name'}),
            'affects_image': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AttributeValueForm(forms.ModelForm):
    class Meta:
        model = AttributeValue
        fields = ['value']
        widgets = {
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter attribute value'}),
        }

