from django.core.management.base import BaseCommand
from inventory.models import Product
import os
import json
import pandas as pd

class Command(BaseCommand):
    help = 'Load products from movie_descriptions.json into the Product model'
    
    def handle(self, *args, **kwargs):
        df = pd.read_csv('products.csv')
        products = json.loads(df.to_json(orient="records"))
        print(products)

        for i in range(len(products)):
            product = products[i]
            exist = Product.objects.filter(name = product['name']).first() 
            if not exist:
                try:              
                    Product.objects.create(
                        name = product['name'],
                        description = product['description'],
                        price = product['price'],
                        quantity = 1,
                        picture = 'default.jpg',
                        )
                except:
                    print('wrong')
                    pass        
