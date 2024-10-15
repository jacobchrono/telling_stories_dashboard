import panel as pn
import numpy as np  # Import numpy
import pandas as pd
import plotly.express as px

# Initialize Panel with Plotly support
pn.extension("plotly")

# Load and clean data
df = pd.read_excel(r'data\\montana_listings.xlsx', sheet_name='in')

# Ensure the dataset has latitude and longitude columns
df_clean = df.dropna(subset=['price', 'odometer', 'make', 'model', 'condition', 
                             'title', 'type', 'transmission', 'drive', 'latitude', 'longitude']).copy()

df_clean['log_odometer'] = np.log(df_clean['odometer'])
df_clean['vehicle_type'] = df_clean['type']

# ===== HELPER FUNCTIONS ===== #
def create_scatter_plot(filtered_data):
    """Generate a scatter plot."""
    fig = px.scatter(
        filtered_data, 
        x='log_odometer', y='price', trendline='ols',
        labels={'log_odometer': 'Log of Odometer', 'price': 'Price'},
        title='Scatter Plot: Price vs Log of Odometer'
    )
    return fig

def create_choropleth_map(filtered_data):
    """Generate a map using latitude and longitude."""
    fig = px.scatter_mapbox(
        filtered_data, 
        lat='latitude', lon='longitude', color='price',
        hover_name='make', zoom=6, height=500,
        title='Map: Vehicle Prices by Location',
        mapbox_style="carto-positron"
    )
    return fig

def filter_data(make=None, model=None, vehicle_type=None, transmission=None, 
                title=None, condition=None):
    """Filter the dataset based on provided criteria."""
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

# Create initial plots
scatter_pane = pn.pane.Plotly(create_scatter_plot(df_clean), height=500, width=700)
map_pane = pn.pane.Plotly(create_choropleth_map(df_clean), height=500, width=700)

# Create widgets with smaller sizes
make_widget = pn.widgets.Select(name='Make', options=[''] + df_clean['make'].unique().tolist(), width=150)
model_widget = pn.widgets.Select(name='Model', options=[''] + df_clean['model'].unique().tolist(), width=150)
vehicle_type_widget = pn.widgets.Select(name='Vehicle Type', options=[''] + df_clean['vehicle_type'].unique().tolist(), width=150)
transmission_widget = pn.widgets.Select(name='Transmission', options=[''] + df_clean['transmission'].unique().tolist(), width=150)
title_widget = pn.widgets.Select(name='Title', options=[''] + df_clean['title'].unique().tolist(), width=150)
condition_widget = pn.widgets.Select(name='Condition', options=[''] + df_clean['condition'].unique().tolist(), width=150)

# Update function to refresh both graphs
def update_graphs(event=None):
    filtered_df = filter_data(
        make=make_widget.value,
        model=model_widget.value,
        vehicle_type=vehicle_type_widget.value,
        transmission=transmission_widget.value,
        title=title_widget.value,
        condition=condition_widget.value
    )
    scatter_pane.object = create_scatter_plot(filtered_df)
    map_pane.object = create_choropleth_map(filtered_df)

# Attach callbacks to widgets
for widget in [make_widget, model_widget, vehicle_type_widget, transmission_widget, title_widget, condition_widget]:
    widget.param.watch(update_graphs, 'value')

# Organize the layout
widgets = pn.Row(make_widget, model_widget, vehicle_type_widget, transmission_widget, title_widget, condition_widget, sizing_mode='fixed')

# Use pn.pane.HTML for styled text (instead of Markdown style)
header = pn.pane.HTML(
    "<h1 style='font-size:24px; text-align:left;'>Vehicle Dashboard: Focus on Montana Listings</h1>"
)

# Create the dashboard layout
dashboard = pn.Column(
    header,
    widgets,  # Widgets at the top
    pn.Row(scatter_pane, map_pane)  # Side-by-side graphs
)

# ===== SERVE THE DASHBOARD ===== #
dashboard.show(port=5006)

# ===== SAVE THE DASHBOARD TO HTML ===== #
# dashboard.save('vehicle_dashboard.html', embed=True)

# print("Dashboard saved as 'vehicle_dashboard.html'. You can open it locally in a browser.")