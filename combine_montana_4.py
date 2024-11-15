import panel as pn
import numpy as np  # Import numpy
import pandas as pd
import plotly.express as px

# Initialize Panel with Plotly support
pn.extension("plotly")

# Load and clean data
df = pd.read_excel(r'data\\montana_listings.xlsx', sheet_name='in')

# Ensure the dataset has latitude and longitude columns
df_clean = df.dropna(subset=['price', 'odometer', 'make', 'model', 
                             'latitude', 'longitude']).copy()

df_clean['log_odometer'] = np.log(df_clean['odometer'])
df_clean['vehicle_type'] = df_clean['type']

# ===== FILTER FOR TOP 5 MAKES AND MODELS ===== #
# Identify the top 5 makes
top_makes = df_clean['make'].value_counts().nlargest(5).index

# Filter the dataset to only include the top 5 makes
df_filtered = df_clean[df_clean['make'].isin(top_makes)]

# For each of the top 5 makes, find the top 5 models
top_models = (
    df_filtered.groupby('make')['model']
    .value_counts()
    .groupby(level=0)
    .nlargest(5)
    .reset_index(level=0, drop=True)
    .index
)

# Filter the dataset to only include the top 5 models within the top 5 makes
df_filtered = df_filtered[df_filtered.set_index(['make', 'model']).index.isin(top_models)]

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

def filter_data(make=None, model=None):
    """Filter the dataset based on selected make and model."""
    filtered_df = df_filtered
    if make:
        filtered_df = filtered_df[filtered_df['make'] == make]
    if model:
        filtered_df = filtered_df[filtered_df['model'] == model]
    return filtered_df

# Update models based on selected make
def update_model_options(event):
    """Update the model options based on the selected make."""
    selected_make = make_widget.value
    if selected_make:
        models = df_filtered[df_filtered['make'] == selected_make]['model'].unique().tolist()
        model_widget.options = [''] + models
    else:
        model_widget.options = ['']

# Create widgets with smaller sizes
make_widget = pn.widgets.Select(name='Make', options=[''] + top_makes.tolist(), width=150)
model_widget = pn.widgets.Select(name='Model', options=[''], width=150)

# Attach callback to update model options when make changes
make_widget.param.watch(update_model_options, 'value')

# Create initial plots
scatter_pane = pn.pane.Plotly(create_scatter_plot(df_filtered), height=500, width=700)
map_pane = pn.pane.Plotly(create_choropleth_map(df_filtered), height=500, width=700)

# Update function to refresh both graphs
def update_graphs(event=None):
    filtered_df = filter_data(make=make_widget.value, model=model_widget.value)
    scatter_pane.object = create_scatter_plot(filtered_df)
    map_pane.object = create_choropleth_map(filtered_df)

# Attach callbacks to widgets
make_widget.param.watch(update_graphs, 'value')
model_widget.param.watch(update_graphs, 'value')

# Organize the layout
widgets = pn.Row(make_widget, model_widget, sizing_mode='fixed')

# Use pn.pane.HTML for styled text (instead of Markdown style)
header = pn.pane.HTML(
    "<h1 style='font-size:24px; text-align:left;'>Vehicle Dashboard: Top Makes and Models</h1>"
)

# Create the dashboard layout
dashboard = pn.Column(
    header,
    widgets,  # Widgets at the top
    pn.Row(scatter_pane, map_pane)  # Side-by-side graphs
)

# ===== SERVE THE DASHBOARD ===== #
# dashboard.show(port=5006)

# ===== SAVE THE DASHBOARD TO HTML ===== #
dashboard.save('vehicle_dashboard.html', embed=True)

print("Dashboard saved as 'vehicle_dashboard.html'. You can open it locally in a browser.")
