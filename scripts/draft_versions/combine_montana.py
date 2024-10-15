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
        hover_name='make', zoom=6, height=400,
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
scatter_pane = pn.pane.Plotly(create_scatter_plot(df_clean), height=400, width=500)
map_pane = pn.pane.Plotly(create_choropleth_map(df_clean), height=400, width=500)

# Create widgets
make_widget = pn.widgets.Select(name='Make', options=[''] + df_clean['make'].unique().tolist())
model_widget = pn.widgets.Select(name='Model', options=[''] + df_clean['model'].unique().tolist())
vehicle_type_widget = pn.widgets.Select(name='Vehicle Type', options=[''] + df_clean['vehicle_type'].unique().tolist())
transmission_widget = pn.widgets.Select(name='Transmission', options=[''] + df_clean['transmission'].unique().tolist())
title_widget = pn.widgets.Select(name='Title', options=[''] + df_clean['title'].unique().tolist())
condition_widget = pn.widgets.Select(name='Condition', options=[''] + df_clean['condition'].unique().tolist())

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
widgets = pn.Row(make_widget, model_widget, vehicle_type_widget, transmission_widget, title_widget, condition_widget)

# Use pn.pane.HTML for styled text (instead of Markdown style)
header = pn.pane.HTML(
    "<h1 style='font-size:24px; text-align:left;'>Vehicle Dashboard</h1>"
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
dashboard.save('vehicle_dashboard.html', embed=True)


'''
version 2:

import panel as pn
import numpy as np  # Import numpy (missed earlier)
import pandas as pd
import plotly.express as px

# Initialize Panel with Plotly support
pn.extension("plotly")

# Load and clean data
df = pd.read_excel(r'data\\montana_listings.xlsx', sheet_name='in')

df_clean = df.dropna(subset=['price', 'odometer', 'make', 'model', 'condition', 
                             'title', 'type', 'transmission', 'drive']).copy()
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
    """Generate a choropleth map."""
    fig = px.choropleth(
        filtered_data, 
        locations='location', locationmode='USA-states',
        color='price', hover_name='make',
        title='Choropleth Map: Vehicle Prices by Region',
        scope='usa'
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
scatter_pane = pn.pane.Plotly(create_scatter_plot(df_clean), height=400, width=500)
choropleth_pane = pn.pane.Plotly(create_choropleth_map(df_clean), height=400, width=500)

# Create widgets
make_widget = pn.widgets.Select(name='Make', options=[''] + df_clean['make'].unique().tolist())
model_widget = pn.widgets.Select(name='Model', options=[''] + df_clean['model'].unique().tolist())
vehicle_type_widget = pn.widgets.Select(name='Vehicle Type', options=[''] + df_clean['vehicle_type'].unique().tolist())
transmission_widget = pn.widgets.Select(name='Transmission', options=[''] + df_clean['transmission'].unique().tolist())
title_widget = pn.widgets.Select(name='Title', options=[''] + df_clean['title'].unique().tolist())
condition_widget = pn.widgets.Select(name='Condition', options=[''] + df_clean['condition'].unique().tolist())

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
    choropleth_pane.object = create_choropleth_map(filtered_df)

# Attach callbacks to widgets
for widget in [make_widget, model_widget, vehicle_type_widget, transmission_widget, title_widget, condition_widget]:
    widget.param.watch(update_graphs, 'value')

# Organize the layout
widgets = pn.Row(make_widget, model_widget, vehicle_type_widget, transmission_widget, title_widget, condition_widget)

# Use pn.pane.HTML for styled text (instead of Markdown style)
header = pn.pane.HTML(
    "<h1 style='font-size:24px; text-align:left;'>Vehicle Dashboard</h1>"
)

# Create the dashboard layout
dashboard = pn.Column(
    header,
    widgets,  # Widgets at the top
    pn.Row(scatter_pane, choropleth_pane)  # Side-by-side graphs
)

# Serve the dashboard
dashboard.show(port=5006)



# version 1
import panel as pn
import pandas as pd
import numpy as np
import plotly.express as px

# Initialize Panel with Plotly support
pn.extension("plotly")

# Load data (replace with your actual data paths if needed)
df = pd.read_excel(r'data\montana_listings.xlsx', sheet_name='in')

# Clean and preprocess the data
df_clean = df.dropna(subset=['price', 'odometer', 'make', 'model', 'condition', 
                             'title', 'type', 'transmission', 'drive']).copy()

df_clean['log_odometer'] = np.log(df_clean['odometer'])
df_clean['vehicle_type'] = df_clean['type']

# ===== HELPER FUNCTION TO CREATE SCATTERPLOT ===== #
def create_scatter_plot(filtered_data):
    """Generates a scatter plot based on filtered data."""
    fig = px.scatter(
        filtered_data, 
        x='log_odometer', y='price', trendline='ols',
        labels={'log_odometer': 'Log of Odometer', 'price': 'Price'},
        title='Scatter Plot: Price vs Log of Odometer'
    )
    return fig

# ===== HELPER FUNCTION TO CREATE CHOROPLETH MAP ===== #
def create_choropleth_map(filtered_data):
    """Generates a choropleth map based on filtered data."""
    fig = px.choropleth(
        filtered_data, 
        locations='location', locationmode='USA-states',
        color='price', hover_name='make', 
        title='Choropleth Map: Vehicle Prices by Region',
        scope='usa'
    )
    return fig

# ===== FILTERING LOGIC ===== #
def filter_data(make=None, model=None, vehicle_type=None, transmission=None, 
                title=None, condition=None):
    """Filters the dataset based on provided criteria."""
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

# ===== INITIAL PLOTS ===== #
scatter_pane = pn.pane.Plotly(create_scatter_plot(df_clean), height=400, width=500)
choropleth_pane = pn.pane.Plotly(create_choropleth_map(df_clean), height=400, width=500)

# ===== FILTER WIDGETS ===== #
make_widget = pn.widgets.Select(name='Make', options=[''] + df_clean['make'].unique().tolist())
model_widget = pn.widgets.Select(name='Model', options=[''] + df_clean['model'].unique().tolist())
vehicle_type_widget = pn.widgets.Select(name='Vehicle Type', options=[''] + df_clean['vehicle_type'].unique().tolist())
transmission_widget = pn.widgets.Select(name='Transmission', options=[''] + df_clean['transmission'].unique().tolist())
title_widget = pn.widgets.Select(name='Title', options=[''] + df_clean['title'].unique().tolist())
condition_widget = pn.widgets.Select(name='Condition', options=[''] + df_clean['condition'].unique().tolist())

# ===== CALLBACK FUNCTION TO UPDATE BOTH GRAPHS ===== #
def update_graphs(event=None):
    """Updates both the scatter plot and the choropleth map based on widget values."""
    # Get current widget values
    filtered_df = filter_data(
        make=make_widget.value,
        model=model_widget.value,
        vehicle_type=vehicle_type_widget.value,
        transmission=transmission_widget.value,
        title=title_widget.value,
        condition=condition_widget.value
    )
    
    # Update both plots with filtered data
    scatter_pane.object = create_scatter_plot(filtered_df)
    choropleth_pane.object = create_choropleth_map(filtered_df)

# Attach the callback to widget value changes
make_widget.param.watch(update_graphs, 'value')
model_widget.param.watch(update_graphs, 'value')
vehicle_type_widget.param.watch(update_graphs, 'value')
transmission_widget.param.watch(update_graphs, 'value')
title_widget.param.watch(update_graphs, 'value')
condition_widget.param.watch(update_graphs, 'value')

# ===== LAYOUT: DASHBOARD ORGANIZATION ===== #
widgets = pn.Row(
    make_widget, model_widget, vehicle_type_widget, 
    transmission_widget, title_widget, condition_widget
)

dashboard = pn.Column(
    pn.pane.Markdown("# Vehicle Dashboard", style={'font-size': '24px', 'text-align': 'left'}),
    widgets,  # Filter widgets at the top
    pn.Row(scatter_pane, choropleth_pane)  # Graphs side-by-side
)

# ===== SERVE THE DASHBOARD ===== #
dashboard.show(port=5006)
'''