from product.models import Category, Brand, Product, ProductVariant, ProductImages, Attribute, AttributeValue, ProductAttribute, VariantAttribute
from django.utils.text import slugify
from django.core.files.base import ContentFile
from PIL import Image
import io

# Clear existing products (preserve categories, brands, attributes)
ProductVariant.objects.all().delete()
ProductImages.objects.all().delete()
ProductAttribute.objects.all().delete()
VariantAttribute.objects.all().delete()
Product.objects.all().delete()

# Create dummy image
def create_dummy_image(filename):
    img = Image.new('RGB', (200, 200), color='gray')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return ContentFile(img_io.read(), name=filename)

# Sample product data
smartphone_data = [
    {
        'name': 'Galaxy S23 Ultra',
        'brand': 'Samsung',
        'description': 'Flagship smartphone with advanced camera',
        'variants': [
            {'color': 'Black', 'storage': '256GB', 'price': 79999.00, 'stock': 50, 'is_default': True},
            {'color': 'Blue', 'storage': '256GB', 'price': 79999.00, 'stock': 40, 'is_default': False},
        ],
    },
    {
        'name': 'iPhone 14 Pro',
        'brand': 'Apple',
        'description': 'Premium smartphone with iOS',
        'variants': [
            {'color': 'Silver', 'storage': '128GB', 'price': 69999.00, 'stock': 40, 'is_default': True},
            {'color': 'Gold', 'storage': '128GB', 'price': 69999.00, 'stock': 30, 'is_default': False},
        ],
    },
    {
        'name': 'Realme 11 Pro',
        'brand': 'Realme',
        'description': 'Mid-range smartphone with fast charging',
        'variants': [
            {'color': 'Black', 'storage': '128GB', 'price': 24999.00, 'stock': 60, 'is_default': True},
            {'color': 'White', 'storage': '128GB', 'price': 24999.00, 'stock': 50, 'is_default': False},
        ],
    },
    {
        'name': 'Vivo V27',
        'brand': 'Vivo',
        'description': 'Stylish smartphone with great display',
        'variants': [
            {'color': 'Blue', 'storage': '256GB', 'price': 32999.00, 'stock': 45, 'is_default': True},
            {'color': 'Silver', 'storage': '256GB', 'price': 32999.00, 'stock': 35, 'is_default': False},
        ],
    },
    {
        'name': 'Oppo Reno 8',
        'brand': 'Oppo',
        'description': 'Camera-focused smartphone',
        'variants': [
            {'color': 'Gold', 'storage': '128GB', 'price': 29999.00, 'stock': 55, 'is_default': True},
            {'color': 'Black', 'storage': '128GB', 'price': 29999.00, 'stock': 45, 'is_default': False},
        ],
    },
]
tablet_data = [
    {
        'name': 'Galaxy Tab S8',
        'brand': 'Samsung',
        'description': 'High-performance tablet',
        'variants': [
            {'color': 'Silver', 'storage': '128GB', 'price': 49999.00, 'stock': 30, 'is_default': True},
            {'color': 'Black', 'storage': '128GB', 'price': 49999.00, 'stock': 25, 'is_default': False},
        ],
    },
    {
        'name': 'iPad Air 5',
        'brand': 'Apple',
        'description': 'Lightweight tablet with M1 chip',
        'variants': [
            {'color': 'Blue', 'storage': '128GB', 'price': 54999.00, 'stock': 25, 'is_default': True},
            {'color': 'Silver', 'storage': '128GB', 'price': 54999.00, 'stock': 20, 'is_default': False},
        ],
    },
    {
        'name': 'Realme Pad',
        'brand': 'Realme',
        'description': 'Affordable tablet for media',
        'variants': [
            {'color': 'Gray', 'storage': '128GB', 'price': 17999.00, 'stock': 50, 'is_default': True},
            {'color': 'Gold', 'storage': '128GB', 'price': 17999.00, 'stock': 40, 'is_default': False},
        ],
    },
    {
        'name': 'Vivo Pad',
        'brand': 'Vivo',
        'description': 'Tablet with vibrant display',
        'variants': [
            {'color': 'Black', 'storage': '128GB', 'price': 25999.00, 'stock': 35, 'is_default': True},
            {'color': 'Blue', 'storage': '128GB', 'price': 25999.00, 'stock': 30, 'is_default': False},
        ],
    },
    {
        'name': 'Oppo Pad Air',
        'brand': 'Oppo',
        'description': 'Slim tablet for portability',
        'variants': [
            {'color': 'Silver', 'storage': '128GB', 'price': 19999.00, 'stock': 40, 'is_default': True},
            {'color': 'Gray', 'storage': '128GB', 'price': 19999.00, 'stock': 35, 'is_default': False},
        ],
    },
]
accessory_data = [
    {
        'name': 'AirPods Pro',
        'brand': 'Apple',
        'description': 'Wireless earbuds with noise cancellation',
        'variants': [
            {'color': 'White', 'type': 'Earbuds', 'price': 24999.00, 'stock': 100, 'is_default': True},
            {'color': 'Black', 'type': 'Earbuds', 'price': 24999.00, 'stock': 80, 'is_default': False},
        ],
    },
    {
        'name': 'Samsung 25W Charger',
        'brand': 'Samsung',
        'description': 'Fast charger for smartphones',
        'variants': [
            {'color': 'Black', 'type': 'Charger', 'price': 1499.00, 'stock': 200, 'is_default': True},
            {'color': 'White', 'type': 'Charger', 'price': 1499.00, 'stock': 180, 'is_default': False},
        ],
    },
    {
        'name': 'Realme Buds',
        'brand': 'Realme',
        'description': 'Budget-friendly earbuds',
        'variants': [
            {'color': 'Black', 'type': 'Earbuds', 'price': 1999.00, 'stock': 150, 'is_default': True},
            {'color': 'Blue', 'type': 'Earbuds', 'price': 1999.00, 'stock': 130, 'is_default': False},
        ],
    },
    {
        'name': 'Vivo Power Bank',
        'brand': 'Vivo',
        'description': '10000mAh power bank',
        'variants': [
            {'color': 'Silver', 'type': 'Power Bank', 'price': 2499.00, 'stock': 120, 'is_default': True},
            {'color': 'Black', 'type': 'Power Bank', 'price': 2499.00, 'stock': 100, 'is_default': False},
        ],
    },
    {
        'name': 'Oppo Phone Case',
        'brand': 'Oppo',
        'description': 'Protective case for Reno series',
        'variants': [
            {'color': 'Blue', 'type': 'Case', 'price': 999.00, 'stock': 180, 'is_default': True},
            {'color': 'Black', 'type': 'Case', 'price': 999.00, 'stock': 160, 'is_default': False},
        ],
    },
]

def create_products(category_name, product_data):
    try:
        category = Category.objects.get(category_name=category_name)
    except Category.DoesNotExist:
        print(f"Category '{category_name}' not found. Skipping.")
        return
    for data in product_data:
        try:
            brand = Brand.objects.get(brand_name=data['brand'])
        except Brand.DoesNotExist:
            print(f"Brand '{data['brand']}' not found. Skipping product '{data['name']}'.")
            continue
        product, created = Product.objects.get_or_create(
            product_name=data['name'],
            category=category,
            brand=brand,
            defaults={
                'product_slug': slugify(data['name']),
                'description': data['description'],
                'is_deleted': False,
            }
        )
        if created:
            # Thumbnail will be set after creating default variant
            pass

        # Create product attributes
        for variant_data in data['variants']:
            color = variant_data['color']
            attr_values = {'Color': color}
            if 'storage' in variant_data:
                attr_values['Storage'] = variant_data['storage']
            if 'type' in variant_data:
                attr_values['Type'] = variant_data['type']
            for attr_name, attr_value in attr_values.items():
                try:
                    attribute = Attribute.objects.get(name=attr_name)
                    attr_value_obj = AttributeValue.objects.get(attribute=attribute, value=attr_value)
                    prod_attr, _ = ProductAttribute.objects.get_or_create(product=product, attribute=attribute)
                    prod_attr.values.add(attr_value_obj)
                except (Attribute.DoesNotExist, AttributeValue.DoesNotExist):
                    print(f"Attribute '{attr_name}' or value '{attr_value}' not found for product '{data['name']}'.")
                    continue

        # Create variants
        for variant_data in data['variants']:
            variant = ProductVariant(
                product=product,
                price=variant_data['price'],
                stock=variant_data['stock'],
                is_default=variant_data['is_default'],
                is_deleted=False,
                reorder_level=5,
            )
            variant.save()

            # Assign variant attributes
            attr_values = {'Color': variant_data['color']}
            if 'storage' in variant_data:
                attr_values['Storage'] = variant_data['storage']
            if 'type' in variant_data:
                attr_values['Type'] = variant_data['type']
            for attr_name, attr_value in attr_values.items():
                try:
                    attribute = Attribute.objects.get(name=attr_name)
                    value = AttributeValue.objects.get(attribute=attribute, value=attr_value)
                    VariantAttribute.objects.get_or_create(variant=variant, attribute_value=value)
                except (Attribute.DoesNotExist, AttributeValue.DoesNotExist):
                    print(f"Attribute '{attr_name}' or value '{attr_value}' not found for variant of '{data['name']}'.")
                    continue

            # Create 4 images per variant (front, back, side, angled)
            angles = ['front', 'back', 'side', 'angled']
            for i, angle in enumerate(angles):
                ProductImages.objects.get_or_create(
                    product=product,
                    variant=variant,
                    defaults={
                        'image': create_dummy_image(f"{slugify(data['name'])}-{variant_data['color'].lower()}-{angle}.jpg"),
                        'is_default': i == 0  # First image (front) is default
                    }
                )

            # Set thumbnail to default variant's front image
            if variant_data['is_default'] and created:
                product.thumbnail.save(
                    f"thumbnail_{slugify(data['name'])}-{variant_data['color'].lower()}.jpg",
                    create_dummy_image(f"thumbnail_{slugify(data['name'])}-{variant_data['color'].lower()}.jpg"),
                    save=True
                )

# Create products
create_products('Smart Phone', smartphone_data)
create_products('Tablets', tablet_data)
create_products('Accessories', accessory_data)

print("Created 15 products: 5 each in Smart Phone, Tablets, Accessories with 2 variants each, 4 images per variant, and thumbnails.")