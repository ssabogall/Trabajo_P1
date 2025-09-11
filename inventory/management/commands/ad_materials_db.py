from django.core.management.base import BaseCommand
from inventory.models import RawMaterial
import os
import json
import pandas as pd

class Command(BaseCommand):
    help = 'Load materials from movie_descriptions.json into the Product model'
    
    def handle(self, *args, **kwargs):
        df = pd.read_csv('materials.csv')
        materials = json.loads(df.to_json(orient="records"))
        print(materials)

        for i in range(len(materials)):
            material = materials[i]
            exist = RawMaterial.objects.filter(name = material['name']).first() 
            if not exist:
                try:              
                    RawMaterial.objects.create(
                        name = material['name'],
                        units = material['units'],
                        exp_date = material['exp_date']
                        )
                except:
                    print('wrong')
                    pass        
