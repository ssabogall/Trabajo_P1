from django.core.management.base import BaseCommand
from inventory.models import Product, RawMaterial, ProductRawMaterial
import os
import json
import pandas as pd

class Command(BaseCommand):
    help = 'Load materials from movie_descriptions.json into the Product model'
    
    def handle(self, *args, **kwargs):
        df = pd.read_csv('products_material.csv')
        materials = json.loads(df.to_json(orient="records"))
        print(materials)

        for i in range(len(materials)):
            material = materials[i]
            product_name = material['product']
            product = Product.objects.get(name=product_name)
            rawMaterial_name = material['material']
            rawMaterial = RawMaterial.objects.get(name=rawMaterial_name) 
            quantity = material['quantity']

            exists = ProductRawMaterial.objects.filter(product=product,material=rawMaterial).exists() 
            if not exists:
                try:     
                    ProductRawMaterial.objects.create(
                    product = product,
                    material = rawMaterial,
                    material_quantity = quantity
                    )
                except:
                    print('wrong')
                    pass 
            
            