import pandas as pd
import statsmodels.api as sm
import numpy as np

# Load and clean the data
df = pd.read_excel(r'data\\carbitrage-data.xlsx', sheet_name='carbitrage-data')
df = df[['make', 'model', 'year', 'odometer', 'price', 'location']].dropna()
df['odometer'] = pd.to_numeric(df['odometer'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df[(df['odometer'] > 0) & (df['price'] > 0)]

# Log transformation and dummies
df['log_odometer'] = np.log(df['odometer'])
make_dummies = pd.get_dummies(df['make'], drop_first=True)
location_dummies = pd.get_dummies(df['location'], drop_first=True)

print(df)