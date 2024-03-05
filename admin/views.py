import datetime
import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from product.models import *
from accounts.models import profile,User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

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
            
    return render(request,'admin/admin_login.html')
def ad_log_out(request):
    logout(request)
    return redirect('admin_login')

def dashboard(request):
    if request.user.is_superuser==False: 
        return redirect('admin_login')
    return render(request,'admin/index.html')


def categories(request):
    category=Category.objects.all()
    context={'category':category}
    return render(request,'admin/categories.html',context)

def add_category(request):
    if request.method=='POST':
        name=request.POST['name']
        image=request.FILES.get('img')
        new_category=Category.objects.create(category_name=name,category_image=image)
        new_category.save()
        
        return redirect('categories')
    
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
    return render(request,'admin/edit_categories.html', context)  
    
def delete_categories(request,pk):
    ct=Category.objects.get(pk=pk)
    os.remove(ct.category_image.path)
    ct.delete()
    return redirect('categories')



def delete_product(request,pk):
    pd=Product.objects.get(pk=pk)
    os.remove(pd.category_image.path)
    pd.delete()
    return redirect('product_list')


def user_list(request):
    user=profile.objects.select_related('user').all()
    
    context={'data':user}
    for i in user:
        print(i.pk)
        print(i.user.pk)
    return render(request,'admin/user_list.html',context)

def block_user(request,pk):
    user=User.objects.get(pk=pk)
    user.is_active=not user.is_active
    user.save()
    return redirect('user_list')







def product_list(request):
    product=Product.objects.all()
    context={'data':product}
    return render(request,'admin/product_list.html',context)

def add_product(request):
    if request.method=='POST':
        pname=request.POST['name']
        pdescription=request.POST['description']
        pbrand=request.POST['brand']
        pprice=request.POST['price']
        pdiscount=request.POST['discount']
        pcategory=request.POST['category']
        pthumbnails=request.POST['thumbnail']
        pimages=request.POST['images']
        print(pname,pdescription,pbrand,pprice,pdiscount,pcategory,pthumbnails)
        cat=Category.objects.get(category_name=pcategory)
        br=Brand.objects.get(brand_name=pbrand)
        nw_product=Product.objects.create(product_name=pname,category=cat,brand=br,discription=pdescription,price=pprice,discount=pdiscount,thumbnail=pthumbnails)
        nw_product.save()
        nw_img=ProductImages.objects.create(product=nw_product,image=pimages)
        nw_img.save()
        print(pname,pdescription,pbrand,pprice,pdiscount,pcategory,pthumbnails)
        return redirect('/') 
        
    return render(request,'admin/add_product.html')