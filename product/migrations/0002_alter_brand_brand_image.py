# Generated by Django 4.2.6 on 2024-02-08 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='brand_image',
            field=models.ImageField(blank=True, null=True, upload_to='brands'),
        ),
    ]
