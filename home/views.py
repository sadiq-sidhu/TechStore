import os
from django.shortcuts import get_object_or_404, redirect, render
from product.models import *
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User


# Create your views here.


def home(request):
    category=Category.objects.all()
    context={'category':category}
    return render(request,'home/index.html',context)




class CategoryView(View):
    def get(self, request, val):
        products=Product.objects.filter(category__category_slug=val)
        for product in products:
            print(product.uid,'crete time:',product.created_at,'\n update time:',product.updated_at)
        return render(request, 'home/list.html',locals())
    


def get_product(request,str):
    context={'prod':get_object_or_404(Product,product_slug=str)}
    print(str)
    return render(request,'home/products.html',context)

def search_product(request):
    if request.method =='POST':
        search=request.POST['search']
        print(search)
        products=Product.objects.filter(product_name__icontains=search)
        return render(request,'home/list.html',locals())

def profile(request):
    user=request.user
    print(user.username)
      
    if request.method=='POST':
        if len(request.FILES)!=0:
            if user.profile.profile_image:
              os.remove(user.profile.profile_image.path) 
            user.profile.profile_image= request.FILES['img']
        email=request.POST['email']
        username=request.POST['username']
        phone=request.POST['phone']
        DOB=request.POST['dob']
        if User.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists')
            return redirect('profile')
        if User.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists')
            return redirect('profile')
        if User.objects.filter(profile__phone=phone).exists():
            messages.warning(request,'Phone number is already already exists')
            return redirect('profile')
        if DOB is None:
            messages.warning(request,'enter Date of birth')
            return redirect('profile') 
        user.username=username
        user.email=email
        user.profile.phone=phone
        user.profile.DOB=DOB            
        user.save()
        user.profile.save()
        return redirect('profile')   
        
      
    context={'user':user}  
    return render(request,'home/profile.html',context)