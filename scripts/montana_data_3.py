# Import necessary libraries
import pandas as pd  # For data manipulation
import numpy as np  # For numerical operations like log transformation
import plotly.express as px  # For interactive visualizations
import statsmodels.api as sm  # For statistical models

# Load your data from an Excel file into a DataFrame
df = pd.read_excel(r'data\montana_listings.xlsx', sheet_name='in')

# Clean the data by removing rows with missing values in critical columns
df_clean = df.dropna(subset=['price', 'odometer', 'make', 'model', 'condition', 
                             'title', 'type', 'transmission', 'drive']).copy()

# Create a new column with the log transformation of the 'odometer' field
df_clean['log_odometer'] = np.log(df_clean['odometer'])

# Rename the 'type' column for clarity
df_clean['vehicle_type'] = df_clean['type']

# Define a function to filter data dynamically based on multiple criteria
def filter_data(make=None, model=None, vehicle_type=None, transmission=None, 
                title=None, condition=None):
    """Filter the dataset based on optional input criteria. Returns a subset DataFrame."""
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

# Create a scatter plot with a trendline using Plotly Express
fig_2 = px.scatter(
    df_clean,
    x='log_odometer',
    y='price',
    trendline='ols',  # Add an Ordinary Least Squares (OLS) trendline
    labels={'log_odometer': 'Log of Odometer', 'price': 'Price'},
    title='Price vs Log of Odometer',
    template='simple_white',  # Use a clean background theme
    opacity=0.7,  # Set transparency for better visibility
)

# Extract R² value from the OLS trendline for model fit evaluation
results = px.get_trendline_results(fig_2).iloc[0]['px_fit_results']
r_squared = results.rsquared

# Update the plot title to include the R² value
fig_2.update_layout(
    title=f'Price vs Log of Odometer (R² = {r_squared:.2f})'
)

# Define dropdown menus with labels for better user understanding
dropdowns = [
    {'label': 'Select Make', 'column': 'make'},
    {'label': 'Select Model', 'column': 'model'},
    {'label': 'Select Vehicle Type', 'column': 'vehicle_type'},
    {'label': 'Select Transmission', 'column': 'transmission'},
    {'label': 'Select Title', 'column': 'title'},
    {'label': 'Select Condition', 'column': 'condition'},
]
# Adjust dropdown menus and buttons
buttons = []
for i, dropdown in enumerate(dropdowns):
    buttons.append({
        'buttons': [
            {
                'method': 'restyle',
                'label': str(option),  # Ensure the label is a string
                'args': [{'x': [filter_data(**{dropdown['column']: option})['log_odometer']],
                          'y': [filter_data(**{dropdown['column']: option})['price']],
                          'mode': 'markers'}]  # Plot only markers
            }
            for option in [''] + df_clean[dropdown['column']].unique().tolist()
        ],
        'direction': 'down',
        'showactive': True,
        'x': 0.15 * i,  # Distribute dropdowns horizontally across the top
        'xanchor': 'left',
        'y': 1.15,  # Move above the plot
        'yanchor': 'top',
        'pad': {'r': 10, 't': 20},  # Add padding for spacing
    })

# Add 'Clear Filters' button at the end
buttons.append({
    'buttons': [
        {
            'method': 'restyle',
            'label': 'Clear Filters',
            'args': [{'x': [df_clean['log_odometer']],
                      'y': [df_clean['price']],
                      'mode': 'markers'}]  # Plot only markers
        }
    ],
    'type': 'buttons',
    'showactive': True,
    'x': 0.90,  # Position it at the end
    'xanchor': 'left',
    'y': 1.15,  # Align with other buttons at the top
    'yanchor': 'top',
})

# Update the layout to reflect changes
fig_2.update_layout(
    updatemenus=buttons,
    title=f'Price vs Log of Odometer (R² = {r_squared:.2f})',
    height=600,  # Adjust height for more compact view
    width=800,   # Set appropriate width
    margin={'t': 150},  # Increase top margin to fit dropdowns and buttons
)

# Save the interactive plot as an HTML file
fig_2.write_html(r'html\dynamic_scatter.html')