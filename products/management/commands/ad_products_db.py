from django.core.management.base import BaseCommand
from inventory.models import Product
import os
import json

class Command(BaseCommand):
    help = 'Load products from movie_descriptions.json into the Product model'

    def handle(self, *args, **kwargs):
        # Construct the full path to the JSON file
        #Recuerde que la consola está ubicada en la carpeta DjangoProjectBase.
        #El path del archivo movie_descriptions con respecto a DjangoProjectBase sería la carpeta anterior
        json_file_path = 'products/management/commands/products.json' 
        
        # Load data from the JSON file
        with open(json_file_path, 'r') as file:
            products = json.load(file)
        
        # Add products to the database
        for i in range(len(products)):
            product = products[i]
            exist = Product.objects.filter(name = product['name']).first() #Se asegura que la película no exista en la base de datos
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
            # else:
            #     try:
            #         exist.title = product["title"]
            #         exist.image = 'product/images/default.jpg'
            #         exist.genre = product["genre"]
            #         exist.year = product["year"]
            #         exist.description = product["plot"]
            #     except:
            #         pass
        #self.stdout.write(self.style.SUCCESS(f'Successfully added {cont} products to the database'))


# name = models.CharField(max_length=100) 
# description = models.TextField(blank=True) 
# price = models.DecimalField(max_digits=7, decimal_places=0) 
# quantity = models.PositiveIntegerField(default=0) 
# picture = models.ImageField( upload_to='') make a csv with this data from a bakery