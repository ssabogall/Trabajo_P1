import pandas as pd
import json
import sys

if len(sys.argv) < 2:
    print("Usage: python run.py <csv_file>")
    sys.exit(1)

csv_file = sys.argv[1]

print(f"Using file: {csv_file}")

df = pd.read_csv(csv_file)

df.to_json(f'{csv_file[:-4]}.json', orient='records')

with open(f'{csv_file[:-4]}.json', 'r') as file:
    movies = json.load(file)

for i in range(100):
    movie = movies[i]
    print(movie)
    break