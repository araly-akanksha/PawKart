import pandas as pd, json

df = pd.read_csv(r'C:\Users\yeshw\Documents\GitHub\PawKart\Datasets\flipkart_pet_products.csv')

with open('data_sample.json', 'w', encoding='utf-8') as f:
    json.dump(df.head(3).to_dict('records'), f, indent=2)

