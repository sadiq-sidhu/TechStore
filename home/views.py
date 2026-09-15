import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from product.models import *
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
from address.models import Address
from cart.models import Wishlist
from django.db.models import Q
from django.template.loader import render_to_string
from django.db.models import Min, Max
from offers.utils import calculate_product_pricing
import logging
logger=logging.getLogger(__name__)


# Create your views here.


def home(request):
    categories=Category.objects.filter(is_deleted=False)
    
        
    context={'categories':categories,}
    return render(request,'home/index.html',context)

# class CategoryView(View):
#     def get(self, request, val):
#         products=Product.objects.filter(category__category_slug=val)
        
#         return render(request, 'home/list.html',locals())
    
def category_view(request, val):
    # Fetch category with related products
    category = get_object_or_404(Category, category_slug=val)
    products = Product.objects.filter(category=category, is_deleted=False).select_related('brand', 'category').prefetch_related('variants')

    # Fetch brands associated with products in this category
    brands = Brand.objects.filter(brand__category=category, is_deleted=False).distinct()

    # Fetch attributes and their values for this category
    try:
        print(f"Category object: {category}, Type: {type(category)}")  # Debug
        attributes = Attribute.objects.filter(
            attribute_products__product__category__uid=category.uid,
            attribute_products__is_deleted=False,
            is_deleted=False
        ).distinct().prefetch_related(
            'values',
            'values__variant_attributes',
            'values__variant_attributes__variant'
        )
        print(f"Attributes found: {[attr.name for attr in attributes]}")  # Debug
    except Exception as e:
        print(f"Error fetching attributes: {e}")
        attributes = Attribute.objects.none()

    attribute_data = []
    for attr in attributes:
        values = [
            {
                'value': val,
                'product_count': ProductVariant.objects.filter(
                    variant_attributes__attribute_value=val,
                    product__category=category,
                    is_deleted=False
                ).distinct().count()
            }
            for val in attr.values.filter(is_deleted=False)
            if ProductVariant.objects.filter(
                variant_attributes__attribute_value=val,
                product__category=category,
                is_deleted=False
            ).exists()
        ]
        if values:
            attribute_data.append({
                'attribute': attr,
                'values': values
            })
        print(f"Attribute {attr.name} values: {[v['value'].value for v in values]}")  # Debug

    # Prefetch offers and images
    now = timezone.now()
    products = products.prefetch_related(
        'product_offers',
        'category__category_offers',
        'brand__brand_offers',
        'variants',
        'variants__image',
        'variants__product__product_offers',
        'variants__product__category__category_offers',
        'variants__product__brand__brand_offers',
        'variants__variant_attributes__attribute_value__attribute'
    )

    # Calculate price range based on variant get_selling_price()
    price_range = {'min_price': None, 'max_price': None}
    variants = ProductVariant.objects.filter(product__in=products, is_deleted=False)
    if variants.exists():
        selling_prices = [v.get_selling_price() for v in variants]
        price_range = {
            'min_price': min(selling_prices) if selling_prices else 0,
            'max_price': max(selling_prices) if selling_prices else 0
        }
        print(f'Price range: {price_range}')

    min_price = request.GET.get('min_price', price_range['min_price'])
    max_price = request.GET.get('max_price', price_range['max_price'])
    brand_filter = request.GET.getlist('brand')
    attribute_filters = {key: request.GET.getlist(key) for key in request.GET if key.startswith('attr_')}
    # Transform selected_attributes into a list for template
    selected_attributes_list = [
        {'uid': key.replace('attr_', ''), 'values': values}
        for key, values in attribute_filters.items()
    ]
    sort = request.GET.get('sort', 'default')
    print(f'Filters: min_price={min_price}, max_price={max_price}, brands={brand_filter}, attributes={attribute_filters}, sort={sort}')

    filtered_products = products
    if brand_filter:
        filtered_products = filtered_products.filter(brand__brand_name__in=brand_filter)
        print(f'After brand filter: {filtered_products.count()} products')

    if attribute_filters:
        for attr_key, attr_values in attribute_filters.items():
            if attr_values:
                attr_id = attr_key.replace('attr_', '')
                filtered_products = filtered_products.filter(
                    variants__variant_attributes__attribute_value__attribute__uid=attr_id,
                    variants__variant_attributes__attribute_value__value__in=attr_values,
                    variants__is_deleted=False
                ).distinct()
        print(f'After attribute filter: {filtered_products.count()} products')

    if min_price and max_price:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            filtered_products = [
                p for p in filtered_products
                if any(min_price <= v.get_selling_price() <= max_price for v in p.variants.filter(is_deleted=False))
            ]
            print(f'After price filter: {len(filtered_products)} products')
        except ValueError:
            print('Invalid price filter values')
            filtered_products = list(filtered_products)
    else:
        filtered_products = list(filtered_products)

    if sort == 'low_to_high':
        filtered_products = sorted(
            filtered_products,
            key=lambda p: min((v.get_selling_price() for v in p.variants.filter(is_deleted=False)), default=0)
        )
        print(f'Sorted low_to_high: {[min((v.get_selling_price() for v in p.variants.filter(is_deleted=False)), default=0) for p in filtered_products]}')
    elif sort == 'high_to_low':
        filtered_products = sorted(
            filtered_products,
            key=lambda p: max((v.get_selling_price() for v in p.variants.filter(is_deleted=False)), default=0),
            reverse=True
        )
        print(f'Sorted high_to_low: {[max((v.get_selling_price() for v in p.variants.filter(is_deleted=False)), default=0) for p in filtered_products]}')
    else:
        filtered_products = list(filtered_products)

    # Prepare product data with variant information and default image
    product_data = []
    for product in filtered_products:
        print(f'Processing product: {product.product_name}')
        variants = product.variants.filter(is_deleted=False)
        default_variant = variants.filter(is_default=True).first() or variants.first()
        if default_variant:
            default_image = default_variant.image.filter(is_default=True, is_deleted=False).first() or default_variant.image.filter(is_deleted=False).first()
            product_data.append({
                'product': product,
                'default_variant': default_variant,
                'default_image': default_image,
                'pricing': {
                    'original_price': float(default_variant.price),
                    'discounted_price': default_variant.get_selling_price(),
                    'total_discount_percentage': default_variant.get_total_discount_percentage(),
                    'has_offer': default_variant.get_total_discount_percentage() > 0
                },
                'has_multiple_variants': variants.count() > 1
            })

    brand_data = [
        {
            'brand': b,
            'product_count': Product.objects.filter(
                brand=b, category=category, is_deleted=False
            ).count()
        } for b in brands
    ]

    # Debug context data
    print(f"Product data: {[p['product'].product_name for p in product_data]}")
    print(f"Brand data: {[b['brand'].brand_name for b in brand_data]}")
    print(f"Attribute data: {[a['attribute'].name for a in attribute_data]}")
    print(f"Product count: {len(product_data)}")

    context = {
        'category': category,
        'products': product_data,
        'brands': brand_data,
        'attributes': attribute_data,
        'min_price': float(min_price) if min_price else price_range['min_price'],
        'max_price': float(max_price) if max_price else price_range['max_price'],
        'price_range': price_range,
        'selected_brands': brand_filter,
        'selected_attributes': selected_attributes_list,
        'sort': sort,
        'product_count': len(product_data)
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_list_html = render_to_string('home/product_list.html', context)
        return JsonResponse({
            'product_list_html': product_list_html,
            'selected_brands': brand_filter,
            'selected_attributes': attribute_filters,
            'product_count': len(product_data),
        })

    return render(request, 'home/store.html', context)

def get_product(request, slug):
    # Fetch product by slug
    product = get_object_or_404(Product, product_slug=slug, is_deleted=False)
    logger.info(f"Fetched product: {product.product_name} (slug: {slug})")

    # Check wishlist status
    wishlist = Wishlist.objects.filter(user=request.user, product=product).exists() if request.user.is_authenticated else False
    logger.debug(f"Wishlist status for user {request.user}: {wishlist}")

    # Get all variants
    all_variants = product.variants.filter(is_deleted=False).prefetch_related(
        Prefetch('variant_attributes', queryset=VariantAttribute.objects.filter(is_deleted=False).select_related('attribute_value__attribute'))
    )

    # Get selected variant
    variant_uid = request.GET.get('variant')
    selected_variant = None
    if variant_uid:
        try:
            selected_variant = all_variants.get(uid=variant_uid)
            logger.info(f"Selected variant: {selected_variant.uid} for product {product.product_name}")
        except ProductVariant.DoesNotExist:
            logger.warning(f"Variant {variant_uid} not found for product {product.product_name}")
    
    if not selected_variant and all_variants.exists():
        selected_variant = all_variants.filter(is_default=True).first() or all_variants.first()
        logger.info(f"Fallback variant: {selected_variant.uid if selected_variant else 'None'} for product {product.product_name}")

    # Prepare variant attributes
    variant_attributes = []
    selected_attributes = set()
    if all_variants.exists():
        try:
            if selected_variant:
                selected_attributes = set(str(attr.attribute_value.uid) for attr in selected_variant.variant_attributes.all())
                logger.debug(f"Selected attributes: {selected_attributes}")
            
            attributes = Attribute.objects.filter(
                attribute_products__product=product,
                attribute_products__is_deleted=False
            ).distinct()
            
            for attr in attributes:
                values = AttributeValue.objects.filter(
                    attribute=attr,
                    variant_attributes__variant__product=product,
                    variant_attributes__is_deleted=False
                ).distinct()
                selected_value = next((v for v in values if str(v.uid) in selected_attributes), None)
                variant_attributes.append({
                    'attribute': attr,
                    'values': values,
                    'selected_value': selected_value
                })
                logger.debug(f"Attribute {attr.name}: {len(values)} values, selected: {selected_value.value if selected_value else 'None'}")
        except Exception as e:
            logger.error(f"Error preparing variant attributes: {e}")
            variant_attributes = []
            selected_attributes = set()

    # Get images
    if selected_variant:
        variant_images = selected_variant.image.filter(is_deleted=False).order_by('display_order')
        if not variant_images.exists():
            variant_images = product.product_image.filter(is_deleted=False).order_by('display_order')
    else:
        variant_images = product.product_image.filter(is_deleted=False).order_by('display_order')
    logger.debug(f"Images count: {len(variant_images)}")

    # Prepare price and discount
    if selected_variant:
        price = selected_variant.get_selling_price()
        original_price = float(selected_variant.price)
        discount_percentage = selected_variant.get_total_discount_percentage()
        is_in_stock = selected_variant.is_in_stock
    else:
        price = product.get_min_price()
        original_price = price  # No discounts applied for products without variants
        discount_percentage = 0
        is_in_stock = True  # Assume in stock if no variants

    context = {
        'prod': product,
        'wishlist': wishlist,
        'selected_variant': selected_variant,
        'variant_attributes': variant_attributes,
        'selected_attributes': selected_attributes,
        'variant_images': variant_images,
        'all_variants': all_variants,
        'price': price,
        'original_price': original_price,
        'discount_percentage': discount_percentage,
        'is_in_stock': is_in_stock,
        'appearance_groups': product.get_appearance_based_variant_groups().values() if all_variants.exists() else []
    }

    logger.info(f"Rendering product_details.html for {product.product_name}, selected variant: {selected_variant.uid if selected_variant else 'None'}")
    return render(request, 'home/product_details.html', context)

def search_product(request):
    if request.method == 'POST':
        search = request.POST.get('search', '')
        print(f"Search query: {search}") 
        products = Product.objects.filter(product_name__icontains=search)
        
        context = {
            'products': products
        }
        return render(request, 'home/list.html', context)
    return render(request, 'home/list.html', {'products': []})

def profile(request):
    pass
    # user=request.user
    # print(user.username)
      
    # if request.method=='POST':
    #     if len(request.FILES)!=0:
    #         if user.profile.profile_image:
    #           os.remove(user.profile.profile_image.path) 
    #         user.profile.profile_image= request.FILES['img']
    #     email=request.POST['email']
    #     username=request.POST['username']
    #     phone=request.POST['phone']
    #     DOB=request.POST['dob']
    #     if User.objects.filter(username=username).exists():
    #         messages.warning(request, 'Username already exists')
    #         return redirect('profile')
    #     if User.objects.filter(email=email).exists():
    #         messages.warning(request, 'Email already exists')
    #         return redirect('profile')
    #     if User.objects.filter(profile__phone=phone).exists():
    #         messages.warning(request,'Phone number is already already exists')
    #         return redirect('profile')
    #     if DOB is None:
    #         messages.warning(request,'enter Date of birth')
    #         return redirect('profile') 
    #     user.username=username
    #     user.email=email
    #     user.profile.phone=phone
    #     user.profile.DOB=DOB            
    #     user.save()
    #     user.profile.save()
    #     return redirect('profile')   
        
    # address=Address.objects.filter(user=user) 
    # context={'user':user,
    #          'address':address
    #          } 
     
    # return render(request,'home/profile.html',context)