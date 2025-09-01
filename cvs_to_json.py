import pandas as pd
import json

# Lee el archivo CSV
df = pd.read_csv('products.csv')

# Guarda el DataFrame como JSON
df.to_json('products.json', orient='records')

with open('products.json', 'r') as file:
    movies = json.load(file)

for i in range(100):
    movie = movies[i]
    print(movie)
    break