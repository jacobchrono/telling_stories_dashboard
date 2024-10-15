import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm

# Load your data
df = pd.read_excel(r'data\montana_listings.xlsx', sheet_name='in')

# Load and clean the data, log transform odometer
df_clean = df.dropna(subset=['price', 'odometer', 'make', 'model', 'condition', 
                             'title', 'type', 'transmission', 'drive']).copy()
df_clean['log_odometer'] = np.log(df_clean['odometer'])
df_clean['vehicle_type'] = df_clean['type']

# Function to filter data dynamically based on multiple criteria
def filter_data(make=None, model=None, vehicle_type=None, transmission=None, 
                title=None, condition=None):
    filtered_df = df_clean
    if make:
        filtered_df = filtered_df[filtered_df['make'] == make]
    if model:
        filtered_df = filtered_df[filtered_df['model'] == model]
    if vehicle_type:
        filtered_df = filtered_df[filtered_df['vehicle_type'] == vehicle_type]
    if transmission:
        filtered_df = filtered_df[filtered_df['transmission'] == transmission]
    if title:
        filtered_df = filtered_df[filtered_df['title'] == title]
    if condition:
        filtered_df = filtered_df[filtered_df['condition'] == condition]
    return filtered_df

# Initialize with complete data and generate the scatter plot with trendline
fig_2 = px.scatter(
    df_clean,
    x='log_odometer',
    y='price',
    trendline='ols',
    labels={'log_odometer': 'Log of Odometer', 'price': 'Price'},
    title='Price vs Log of Odometer',
    template='simple_white',
    opacity=0.7,
)

# Extract R² value from the OLS trendline
results = px.get_trendline_results(fig_2).iloc[0]['px_fit_results']
r_squared = results.rsquared

# Add R² value to the plot title
fig_2.update_layout(
    title=f'Price vs Log of Odometer (R² = {r_squared:.2f})'
)

# Define the dropdown menus
dropdowns = [
    {'label': 'Make', 'column': 'make', 'x': 0.15},
    {'label': 'Model', 'column': 'model', 'x': 0.30},
    {'label': 'Vehicle Type', 'column': 'vehicle_type', 'x': 0.45},
    {'label': 'Transmission', 'column': 'transmission', 'x': 0.60},
    {'label': 'Title', 'column': 'title', 'x': 0.75},
    {'label': 'Condition', 'column': 'condition', 'x': 0.90},
]

# Create buttons for the dropdowns
buttons = []
for dropdown in dropdowns:
    buttons.append({
        'buttons': [{'method': 'restyle',
                     'label': str(option),  # Ensure the label is a string
                     'args': [{'x': [filter_data(**{dropdown['column']: option})['log_odometer']],
                               'y': [filter_data(**{dropdown['column']: option})['price']],
                               'mode': 'markers'}]}  # Ensure only markers are shown
                    for option in [''] + df_clean[dropdown['column']].unique().tolist()],
        'direction': 'down',
        'showactive': True,
        'x': dropdown['x'],
        'xanchor': 'left',
        'y': -0.1,  # Move to the bottom
        'yanchor': 'top',
    })

# Add a Clear Filters button
buttons.append({
    'buttons': [
        {
            'method': 'restyle',
            'label': 'Clear Filters',
            'args': [{'x': [df_clean['log_odometer']],
                      'y': [df_clean['price']],
                      'mode': 'markers'}]  # Ensure only markers are shown
        }
    ],
    'type': 'buttons',
    'showactive': True,
    'x': 0.05,
    'xanchor': 'left',
    'y': -0.1,  # Position at the bottom
    'yanchor': 'top',
})

# Update the layout with all dropdowns and buttons
fig_2.update_layout(
    updatemenus=buttons,
    title=f'Price vs Log of Odometer (R² = {r_squared:.2f})',
    margin={'t': 50},  # Adjust top margin to leave space for the title
)

# Save the interactive plot as HTML
fig_2.write_html(r'html\dynamic_scatter.html')
