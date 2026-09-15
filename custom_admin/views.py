import datetime
import json
import os
import uuid
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from product.models import *
from accounts.models import profile,User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from cart.models import Payment,Cart,OrderPlaced,OrderProduct,STATUS_CHOICES
from coupon.models import Coupon,CouponUsage
from django.db.models import Count,Q,Max,Sum,Min,Exists, OuterRef,Prefetch,Subquery
from .forms import *
from wallet.models import Wallet,WalletTransaction
from offers.models import ProductOffer,CategoryOffer,BrandOffer
from PIL import Image
from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from io import BytesIO
import time

# Create your views here.

def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('dashboard')
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        usr=User.objects.filter(username=username)
        if not usr.exists():
            messages.warning(request,'Not found the Username.!')
            return redirect('admin_login')
        user=authenticate(request,username=username,password=password)
        if user is not None and user.is_superuser:
            login(request,user)
            return redirect('dashboard')
        else:
            if user is None:
                messages.warning(request,'Invalid Password!.')
            else:
                messages.warning(request,'User is not Admin.!')
            return redirect('admin_login')
            
    return render(request,'custom_admin/admin_login.html')

@login_required
def ad_log_out(request):
    logout(request)
    
    return redirect('admin_login')

@login_required
def dashboard(request):
    if request.user.is_superuser==False: 
        return redirect('admin_login')
    
    return render(request,'custom_admin/index.html')


@login_required
def categories(request):
    category=Category.objects.filter(is_deleted=False)
    context={'category':category}
    
    return render(request,'custom_admin/categories.html',context)

@login_required
def add_category(request):
    if request.method=='POST':
        name=request.POST['name']
        image=request.FILES.get('img')
        new_category=Category.objects.create(category_name=name,category_image=image)
        new_category.save()
        
        return redirect('categories')
 
@login_required   
def edit_categories(request,pk):
    cat=Category.objects.get(pk=pk)
    if request.method=='POST':
        if len(request.FILES)!=0:
            if len(cat.category_image) >0:
              os.remove(cat.category_image.path) 
            cat.category_image= request.FILES['img']
        cat.category_name=request.POST['name']
        cat.save()
        return redirect('categories')
            
    context={'cat':cat}
    return render(request,'custom_admin/edit_categories.html', context)  

@login_required   
def delete_categories(request,pk):
    ct=Category.objects.get(pk=pk)
    ct.is_deleted=True
    ct.save()
    
    return redirect('categories')




@login_required
def user_list(request):
    user=profile.objects.select_related('user').all()
    context={'data':user} 
       
    return render(request,'custom_admin/user_list.html',context)

@login_required
def block_user(request,pk):
    user=User.objects.get(pk=pk)
    user.is_active=not user.is_active
    user.save()
    
    return redirect('user_list')

@login_required
def user_details(request,pk):
    # profile = Profile.objects.select_related('user').get(user_id=pk)
    user=User.objects.select_related('profile','wallet').prefetch_related('address_set').get(pk=pk)
    orders=OrderPlaced.objects.filter(user=user).select_related('address','payment').prefetch_related('product','orderproduct_set').order_by('-created_at')
    wallet_balance=user.wallet.balance if hasattr(user,'wallet') else 0.00
    total_spend=Payment.objects.filter(user=user,paid=True).aggregate(total=Sum('amount'))['total'] or 0.0
    for i in orders:
        for j in i.orderproduct_set.all():
            print(j.status)
            
    total_orders=orders.count()
    completed_order=orders.filter(orderproduct__status='success').count()
    canceld_order=orders.filter(orderproduct__status='canceled').count()
    print('cancel: ',canceld_order,'complete: ',completed_order)
    # max used to find max value, in here to find most recent value 
    last_order_date=orders.aggregate(created_at_max=Max('created_at'))['created_at_max']
    
    order_id=request.GET.get('order_id','').strip()
    status=request.GET.get('status','')
    date=request.GET.get('date','')
    print('order_id--',order_id,'   status==',status,'   date==',date)
    if order_id:
        orders=orders.filter(id__contains=order_id)
    if status:
        orders=orders.filter(orderproduct__status=status)
    if date:
        orders=orders.filter(created_at__date=date)
    
    
    context={'user':user,
             'orders':orders.distinct(),
             'last_order_date':last_order_date,
             'wallet_balance':wallet_balance,
             'total_spend':total_spend,
             'total_orders':total_orders,
             'completed_order':completed_order,
             'canceld_order':canceld_order,
             
             'status_choices':dict(STATUS_CHOICES),
             'search_id':order_id,
             'search_status':status,
             'search_date':date,
             
             }
    return render(request,'custom_admin/user_details.html',context)


################################

@login_required
def product_list(request):
    variants_queryset = ProductVariant.objects.filter(is_deleted=False).select_related('product')
    default_image_queryset = ProductImages.objects.filter(is_default=True, is_deleted=False)
    products = Product.objects.filter(is_deleted=False).select_related('category', 'brand').prefetch_related(
        Prefetch('variants', queryset=variants_queryset, to_attr='active_variants'),
        Prefetch('product_image', queryset=default_image_queryset, to_attr='default_image')
    )
    
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(product_name__icontains=search_query)
    
    category_filter = request.GET.get('category', '')
    if category_filter:
        products = products.filter(category__category_name=category_filter)
    
    sort_option = request.GET.get('sort', 'latest')
    if sort_option == 'cheap':
        products = products.annotate(min_price=Min('variants__price')).order_by('min_price')
    else:
        products = products.order_by('-created_at')
    
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.filter(is_deleted=False)
    
    return render(request, 'custom_admin/product_list.html', {
        'data': page_obj,
        'categories': categories,
    })

@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            product.attributes.set(form.cleaned_data['applicable_attributes'])
            messages.success(request, 'Product created successfully!')
            return redirect('product_manage_variants', product_id=product.uid)
    else:
        form = ProductForm()
    
    return render(request, 'custom_admin/product_form.html', {
        'form': form,
        'title': 'Add Product'
    })

@login_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, uid=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            product.attributes.set(form.cleaned_data['applicable_attributes'])
            messages.success(request, 'Product updated successfully!')
            return redirect('product_manage_variants', product_id=product.uid)
    else:
        form = ProductForm(instance=product, initial={
            'applicable_attributes': product.attributes.all()
        })
    
    return render(request, 'custom_admin/product_form.html', {
        'form': form,
        'title': 'Edit Product'
    })

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, uid=product_id)
    if request.method == 'POST':
        product.soft_delete()
        messages.success(request, f'Product "{product.product_name}" has been soft deleted.')
        return redirect('product_list')
    return redirect('product_list')

@login_required
def product_manage_variants(request, product_id):
    product = get_object_or_404(Product, uid=product_id)
    variant_groups = {}
    
    try:
        variant_groups = product.get_appearance_based_variant_groups()
    except Exception as e:
        messages.error(request, f"Error grouping variants: {str(e)}")
    
    if request.method == 'POST':
        # Handle variant group deletion
        if 'delete_group' in request.POST:
            group_hash = request.POST.get('group_hash')
            try:
                if variant_groups and int(group_hash) in variant_groups:
                    group = variant_groups[int(group_hash)]
                    # Soft delete all variants in the group
                    for variant in group['variants']:
                        variant.delete()
                    messages.success(request, "Variant group deleted successfully")
                    return redirect('product_manage_variants', product_id=product.uid)
                else:
                    messages.error(request, "Variant group not found")
            except (ValueError, Exception) as e:
                messages.error(request, f"Error deleting variant group: {str(e)}")
        
        # Handle new variant creation
        elif 'add_variant' in request.POST:
            variant_form = VariantCreationForm(request.POST, product=product)
            if variant_form.is_valid():
                try:
                    variant = variant_form.save(commit=False)
                    variant.product = product
                    variant.save()
                    
                    # Save attribute values for this variant
                    for attribute in product.attributes.all():
                        value = variant_form.cleaned_data[f'attr_{attribute.uid}']
                        VariantAttribute.objects.create(
                            variant=variant,
                            attribute_value=value
                        )
                    
                    messages.success(request, 'Variant added successfully!')
                    return redirect('product_manage_variants', product_id=product.uid)
                except Exception as e:
                    messages.error(request, f"Error saving variant: {str(e)}")
            else:
                messages.error(request, "Please correct the errors below")
        else:
            variant_form = VariantCreationForm(product=product)
    else:
        variant_form = VariantCreationForm(product=product)
    
    return render(request, 'custom_admin/product_variants.html', {
        'product': product,
        'variant_groups': variant_groups.values() if variant_groups else [],
        'variant_form': variant_form
    })

@login_required
def variant_group_images(request, product_id, group_hash):
    product = get_object_or_404(Product, uid=product_id)
    variant_groups = product.get_appearance_based_variant_groups()
    group = variant_groups.get(int(group_hash))
    
    if not group:
        raise Http404("Variant group not found")
    
    representative_variant = group['variants'][0]
    images = representative_variant.image.filter(is_deleted=False)
    
    if request.method == 'POST':
        if 'upload_image' in request.POST:
            form = ProductImageForm(request.POST, request.FILES, variant=representative_variant)
            if form.is_valid():
                try:
                    x = float(request.POST.get('x', 0))
                    y = float(request.POST.get('y', 0))
                    width = float(request.POST.get('width', 0))
                    height = float(request.POST.get('height', 0))
                    
                    image_file = request.FILES['image']
                    img = Image.open(image_file)
                    if image_file.content_type == 'image/jpeg' and img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    cropped_img = img.crop((x, y, x + width, y + height))
                    buffer = BytesIO()
                    if image_file.content_type == 'image/jpeg':
                        cropped_img.save(buffer, format='JPEG', quality=90)
                    else:
                        cropped_img.save(buffer, format='PNG', quality=90)
                    buffer.seek(0)
                    
                    image = ProductImages(
                        product=product,
                        variant=representative_variant,
                        is_default=form.cleaned_data['is_default'],
                        display_order=form.cleaned_data['display_order']
                    )
                    
                    timestamp = int(time.time())
                    ext = 'jpg' if image_file.content_type == 'image/jpeg' else 'png'
                    filename = f"{product.product_slug}_{timestamp}.{ext}"
                    image.image.save(filename, ContentFile(buffer.read()), save=True)
                    
                    for variant in group['variants']:
                        if variant != representative_variant:
                            new_image = ProductImages(
                                product=product,
                                variant=variant,
                                image=image.image,
                                is_default=image.is_default,
                                display_order=image.display_order
                            )
                            new_image.save()
                        
                        for attr in variant.get_appearance_attributes():
                            ProductImageAttribute.objects.get_or_create(
                                image=image if variant == representative_variant else new_image,
                                attribute_value=attr.attribute_value
                            )
                    
                    messages.success(request, "Image added to all variants in this group")
                    return redirect('variant_group_images', product_id=product_id, group_hash=group_hash)
                except Exception as e:
                    messages.error(request, f"Error processing image: {str(e)}")
        
        elif 'delete_image' in request.POST:
            image_id = request.POST.get('image_id')
            try:
                image = ProductImages.objects.get(uid=image_id)
                image.delete()
                messages.success(request, "Image deleted successfully")
                return redirect('variant_group_images', product_id=product_id, group_hash=group_hash)
            except ProductImages.DoesNotExist:
                messages.error(request, "Image not found")
        
        elif 'set_default' in request.POST:
            image_id = request.POST.get('image_id')
            try:
                ProductImages.objects.filter(variant__in=group['variants'], is_default=True).update(is_default=False)
                ProductImages.objects.filter(uid=image_id).update(is_default=True)
                messages.success(request, "Default image updated")
                return redirect('variant_group_images', product_id=product_id, group_hash=group_hash)
            except Exception as e:
                messages.error(request, f"Error setting default image: {str(e)}")
    
    form = ProductImageForm(variant=representative_variant)
    
    return render(request, 'custom_admin/variant_group_images.html', {
        'product': product,
        'group': group,
        'images': images,
        'form': form,
        'variant_names': ", ".join(v.get_variant_name() for v in group['variants'])
    })
    
    
@login_required
def variant_edit(request, variant_id):
    variant = get_object_or_404(ProductVariant, uid=variant_id)
    
    if request.method == 'POST':
        form = VariantEditForm(request.POST, instance=variant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variant updated successfully!')
            return redirect('product_manage_variants', product_id=variant.product.uid)
    else:
        form = VariantEditForm(instance=variant)
    
    return render(request, 'custom_admin/variant_edit.html', {
        'form': form,
        'variant': variant
    })

@login_required
def variant_delete(request, variant_id):
    variant = get_object_or_404(ProductVariant, uid=variant_id)
    product_id = variant.product.uid
    variant.soft_delete()
    messages.success(request, 'Variant deleted successfully!')
    return redirect('product_manage_variants', product_id=product_id)

# @login_required
# def variant_image_manage(request, variant_id):
#     variant = get_object_or_404(ProductVariant, uid=variant_id)
#     images = variant.image.filter(is_deleted=False)
    
#     return render(request, 'custom_admin/variant_images.html', {
#         'variant': variant,
#         'images': images
#     })

# @login_required
# def variant_image_add(request, variant_id):
#     variant = get_object_or_404(ProductVariant, uid=variant_id)
    
#     # Prepare the image-affecting attributes in the view
#     image_attrs = variant.variant_attributes.filter(
#         attribute_value__attribute__affects_image=True
#     ).select_related('attribute_value', 'attribute_value__attribute')
    
#     if request.method == 'POST':
#         form = ProductImageForm(request.POST, request.FILES, variant=variant)
#         if form.is_valid():
#             image = form.save(commit=False)
#             image.variant = variant
#             image.product = variant.product
#             image.save()
            
#             # Handle image attribute associations
#             for attr in image_attrs:
#                 if form.cleaned_data.get(f'attr_{attr.uid}'):
#                     ProductImageAttribute.objects.create(
#                         image=image,
#                         attribute_value=attr.attribute_value
#                     )
            
#             messages.success(request, 'Image added successfully!')
#             return redirect('variant_image_manage', variant_id=variant.uid)
#     else:
#         form = ProductImageForm(variant=variant)
    
#     # Prepare a list of attribute data including checked status
#     attribute_data = []
#     for attr in image_attrs:
#         attribute_data.append({
#             'id': attr.uid,
#             'name': f"{attr.attribute_value.attribute.name}: {attr.attribute_value.value}",
#             'checked': form.data.get(f'attr_{attr.uid}') == 'on' if form.is_bound else False
#         })
    
#     return render(request, 'custom_admin/variant_image_add.html', {
#         'form': form,
#         'variant': variant,
#         'attribute_data': attribute_data
#     })

# @login_required
# def variant_image_delete(request, image_id):
#     try:
#         image = get_object_or_404(ProductImages, uid=image_id)
#         variant_id = image.variant.uid
#         image.delete()
#         messages.success(request, 'Image deleted successfully!')
#     except ProductImages.DoesNotExist:
#         messages.error(request,'Image not found')
#     return redirect('variant_image_manage', variant_id=variant_id)

@login_required
def attribute_list(request):
    attributes = Attribute.objects.all()
    return render(request, 'custom_admin/attribute_list.html', {'attributes': attributes})

@login_required
def attribute_add(request):
    if request.method == 'POST':
        form = AttributeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('attribute_list')
    else:
        form = AttributeForm()
    return render(request, 'custom_admin/attribute_form.html', {'form': form, 'title': 'Add Attribute'})

@login_required
def attribute_edit(request, attribute_id):
    attribute = get_object_or_404(Attribute, uid=attribute_id)
    if request.method == 'POST':
        form = AttributeForm(request.POST, instance=attribute)
        if form.is_valid():
            form.save()
            return redirect('attribute_list')
    else:
        form = AttributeForm(instance=attribute)
    return render(request, 'custom_admin/attribute_form.html', {'form': form, 'title': 'Edit Attribute'})

@login_required
def attribute_value_add(request, attribute_id):
    attribute = get_object_or_404(Attribute, uid=attribute_id)
    if request.method == 'POST':
        form = AttributeValueForm(request.POST)
        if form.is_valid():
            attribute_value = form.save(commit=False)
            attribute_value.attribute = attribute
            attribute_value.save()
            return redirect('attribute_list')
    else:
        form = AttributeValueForm()
    return render(request, 'custom_admin/attribute_value_form.html', {
        'form': form,
        'attribute': attribute,
        'title': 'Add Attribute Value'
    })

@login_required
def attribute_value_edit(request, attribute_value_id):
    attribute_value = get_object_or_404(AttributeValue, uid=attribute_value_id)
    if request.method == 'POST':
        form = AttributeValueForm(request.POST, instance=attribute_value)
        if form.is_valid():
            form.save()
            return redirect('attribute_list')
    else:
        form = AttributeValueForm(instance=attribute_value)
    return render(request, 'custom_admin/attribute_value_form.html', {
        'form': form,
        'attribute': attribute_value.attribute,
        'title': 'Edit Attribute Value'
    })



######################################################################################
    


@login_required
def orders(request):
    orders=OrderPlaced.objects.select_related('payment','address','user').annotate(
        total_count=Count('orderproduct'),
        non_canceled_product=Count('orderproduct',filter=~Q(orderproduct__status='canceled'))
    )
    for order in orders:
        order.is_fully_canceled=(order.non_canceled_product==0)
    
    context={'orders':orders}
    return render(request,'custom_admin/orders.html',context)

@login_required
def order_details(request,pk):
    orders=get_object_or_404(OrderPlaced.objects.prefetch_related('payment','address','user'),pk=pk)
    order_products = OrderProduct.objects.filter(orders=orders).select_related('product')
    context={'orders':orders,
             'order_product':order_products,
             'status_choice':STATUS_CHOICES}
    return render(request,'custom_admin/orders_details.html',context)

@login_required
def change_order_status(request, order_uid):
    if request.method == 'POST':
        order = get_object_or_404(OrderPlaced, uid=order_uid)
        new_status = request.POST.get('status')
        
        valid_status=[choice[0] for choice in STATUS_CHOICES]
        
        if new_status in valid_status:
            order_products = OrderProduct.objects.filter(orders=order).select_related('product')  
            for item in order_products:
                if item.status!='canceled':
                    item.status = new_status
                    item.save()
                    
            if new_status == 'delivered' and order.payment.payment_method=='cod':
                order.payment.payment_status = 'success'
                order.payment.paid = True
                order.payment.save()  
                
            messages.success(request, 'Order status updated successfully.')
        else:
            messages.error(request, 'Please select a valid status.')
            
    return redirect('order_details',pk=order_uid)

@login_required
def coupon_list(request):
    coupons=Coupon.objects.annotate(usage_count=Count('couponusage'))
    return render(request,'custom_admin/coupon_list.html',{'coupons':coupons})

@login_required
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Coupon added successfully.')
            return redirect('coupon_list')
    else:
        form = CouponForm()
    return render(request,'custom_admin/coupon_form.html',{'form':form})

@login_required
def edit_coupon(request,coupon_id):
    coupon=get_object_or_404(Coupon,id=coupon_id)
    if request.method == 'POST':
        form=CouponForm(request.POST,instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request,'Coupon updated successfully.')
            return redirect('coupon_list')
    else:
        form=CouponForm(instance=coupon)
    return render(request,'custom_admin/coupon_form.html',{'form':form})

@login_required
def delete_coupon(request,coupon_id):
    coupon=get_object_or_404(Coupon,id=coupon_id)
    if CouponUsage.objects.filter(coupon=coupon).exists():
        messages.error(request,'Cannot delete an applied coupon.')
    else:
        coupon.delete()
        messages.success(request,'Coupon deleted successfully.')
    return redirect('coupon_list')

@login_required
def offer_list(request):
    product_offers=ProductOffer.objects.all()
    category_offers=CategoryOffer.objects.all()
    brand_offers=BrandOffer.objects.all()
    context={
        'product_offers':product_offers,
        'category_offers':category_offers,
        'brand_offers':brand_offers
    }
    return render(request,'custom_admin/offer_list.html',context)

@login_required
def add_product_offer(request):
    if request.method=='POST':
        form=ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('offer_list')
    else:
        form=ProductOfferForm()
    context={'form':form,'offer_type':'Product Offer'}
    return render(request,'custom_admin/add_offer.html',context)

@login_required
def add_category_offer(request):
    if request.method == 'POST':
        form=CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('offer_list')
    else:
        form=ProductOfferForm()
    context={'form':form,'offer_type':'Category Offer'}
    return render(request,'custom_admin/add_offer.html',context)  

@login_required
def add_brand_offer(request):
    if request.method == 'POST':
        form =BrandOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('offer_list')
    else:
        form=BrandOfferForm()
    context={'form':form,'offer_type':'Brand Offer'}
    return render(request,'custom_admin/add_offer.html',context) 

@login_required
def edit_product_offer(request,pk):
    offer=get_object_or_404(ProductOffer,pk=pk)
    if request.method == 'POST':
        form=ProductOfferForm(request.POST,instance=offer)
        form.save()
        return redirect('offer_list')
    else:
        form=ProductOfferForm(instance=offer)
    context={'form':form, 'offer_type':'Product Offer','offer':offer}
    return render(request,'custom_admin/edit_offer.html',context)

@login_required
def edit_category_offer(request,pk):
    offer = get_object_or_404(CategoryOffer,pk=pk)
    if request.method == 'POST':
        form=CategoryOfferForm(request.POST,instance=offer)
        if form.is_valid():
            form.save()
            return redirect('offer_list')
    else:
        form=CategoryOfferForm(instance=offer)
    context={'form':form, 'offer_type':'Category Offer','offer':offer}
    return render(request, 'custom_admin/edit_offer.html',context)

@login_required
def edit_brand_offer(request,pk):
    offer = get_object_or_404(BrandOffer,pk=pk)
    if request.method == 'POST':
        form = BrandOfferForm(request.POST,instance=offer)
        if form.is_valid():
            form.save()
            return redirect('offer_list')
    else:
        form=BrandOfferForm(instance=offer)
    context={'form':form,'offer_type':'Brand Offer','offer':offer}
    return render(request,'custom_admin/edit_offer.html',context)

@login_required
def delete_product_offer(request,pk):
    offer=get_object_or_404(ProductOffer,pk=pk)
    offer.delete()
    return redirect('offer_list')

@login_required
def delete_category_offer(request,pk):
    offer=get_object_or_404(CategoryOffer,pk=pk)
    offer.delete()
    return redirect('offer_list')

@login_required
def delete_brand_offer(request,pk):
    offer=get_object_or_404(BrandOffer,pk=pk)
    offer.delete()
    return redirect('offer_list')
