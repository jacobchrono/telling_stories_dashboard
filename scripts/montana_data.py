import pandas as pd
import plotly.express as px
import numpy as np


# Load your data
df = pd.read_excel(r'data\montana_listings.xlsx', sheet_name='in')

# question 1 are there any places where the model significantly missed?

# Ensure relevant columns are numeric and drop NaNs in 'residual'
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
df['residual'] = pd.to_numeric(df['residual'], errors='coerce')
cleaned_data = df.dropna(subset=['residual']).copy()  # Use .copy() to avoid the warning

# Safely convert make and model to string
cleaned_data.loc[:, 'make'] = cleaned_data['make'].astype(str)
cleaned_data.loc[:, 'model'] = cleaned_data['model'].astype(str)

# Aggregate average residuals
aggregated_data = cleaned_data.groupby(
    ['latitude', 'longitude', 'make', 'model'], as_index=False)['residual'].mean()
aggregated_data.rename(columns={'residual': 'avg_residual'}, inplace=True)

# Plot the average residuals with adjusted zoom and marker size
fig = px.scatter_mapbox(
    aggregated_data,
    lat='latitude',
    lon='longitude',
    color='avg_residual',
    color_continuous_scale='Cividis', # color blind friendly
    range_color=[-30000, 30000],  # Adjust the color bar rang
    title='Average Residuals by Location',
    labels={'avg_residual': 'Average Residual'},
    zoom=6,  # Closer zoom level for Montana
    center={'lat': 46.87, 'lon': -110.36},
    size_max=15  # Adjust the maximum size of the markers
)

fig.update_traces(marker=dict(size=4))  # Make points larger

# Update layout and marker size
fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0, "t":0, "l":0, "b":0},  # Remove unnecessary margins
    showlegend=True
)

fig.write_html(r'html\resid_map.html')
