from .models import Category,Brand
def category_links(request):
    links=Category.objects.all()
    return dict(cat=links)

def brand_links(request):
    links=Brand.objects.all()
    return dict(brand=links)