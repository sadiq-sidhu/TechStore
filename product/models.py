from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
# Create your models here.

class Category(BaseModel):
    category_name=models.CharField(max_length=100)
    category_slug=models.SlugField(unique=True, null=True, blank=True)
    category_image=models.ImageField(upload_to='categries')
    
    def save(self, *args, **kwargs):
        self.category_slug=slugify(self.category_name)
        super(Category ,self).save(*args, **kwargs)
        
    def __str__(self):
        return self.category_name
    
        
        
        
class Brand(BaseModel):
    brand_name=models.CharField(max_length=50)
    brand_slug=models.SlugField(unique=True, null= True, blank=True)
    brand_image=models.ImageField(upload_to='brands' ,null=True, blank=True)
    
    def save(self, *args, **kwargs):
        self.brand_slug=slugify(self.brand_name)
        super(Brand ,self).save(*args, **kwargs)
        
    def __str__(self) -> str:
        return self.brand_name
        
 



class Product(BaseModel):
    product_name=models.CharField(max_length=150)
    product_slug =models.SlugField(unique=True, null=True , blank= True)
    category=models.ForeignKey(Category ,on_delete=models.CASCADE, related_name='product')
    brand=models.ForeignKey(Brand , on_delete=models.CASCADE, related_name='brand')
    discription=models.TextField()
    price=models.FloatField()
    discount=models.FloatField()
    thumbnail=models.ImageField(upload_to='thumbnail',null=True)
    
    
    def save(self, *args, **kwargs):
        self.product_slug=slugify(self.product_name)
        super(Product ,self).save(*args, **kwargs)
        
    def __str__(self) -> str:
        return self.product_name
    
class ProductImages(BaseModel):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_image')
    image= models.ImageField(upload_to='product')
    
