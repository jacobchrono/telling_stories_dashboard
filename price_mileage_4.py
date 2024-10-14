import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import statsmodels.api as sm

# Load and clean the data
df = pd.read_excel(r'data\\carbitrage-data.xlsx', sheet_name='carbitrage-data')
df = df[['make', 'model', 'year', 'odometer', 'price', 'location']].dropna()
df['odometer'] = pd.to_numeric(df['odometer'], errors='coerce')
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# Remove invalid entries
df = df[(df['odometer'] > 0) & (df['price'] > 0)]
df['log_odometer'] = np.log(df['odometer'])  # Add log of mileage

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Price vs. Log of Mileage Dashboard", style={'textAlign': 'center'}),

    # Dropdowns for make, model, year, and location filters
    html.Div([
        html.Label("Select Model:"),
        dcc.Dropdown(
            id='model-dropdown',
            options=[{'label': model, 'value': model} for model in df['model'].unique()],
            value=None,
            multi=True
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Make:"),
        dcc.Dropdown(id='make-dropdown', multi=True),
    ], style={'width': '20%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(id='year-dropdown', multi=True),
    ], style={'width': '20%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Location:"),
        dcc.Dropdown(id='location-dropdown', multi=True),
    ], style={'width': '20%', 'display': 'inline-block'}),

    # Outlier exclusion options
    html.Div([
        html.Label("Outlier Exclusion:"),
        dcc.RadioItems(
            id='outlier-exclusion',
            options=[
                {'label': 'Exclude > $1M', 'value': '1M'},
                {'label': 'Exclude by Std Dev', 'value': 'std'}
            ],
            value=None
        ),
        dcc.Input(id='std-dev-input', type='number', placeholder='Std Dev', style={'marginLeft': '10px'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Checkbox to add regression line
    html.Div([
        dcc.Checklist(
            id='regression-checkbox',
            options=[{'label': 'Show Regression Line', 'value': 'regression'}],
            value=[]
        ),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Graph to display results
    dcc.Graph(id='scatter-plot'),

    # Table for regression info
    html.Div(id='regression-info', style={'marginTop': '30px', 'textAlign': 'center'})
])

# Helper function to filter data based on outlier exclusion
def filter_outliers(data, option, std_dev=None):
    if option == '1M':
        return data[data['price'] <= 1_000_000]
    elif option == 'std' and std_dev is not None:
        mean = data['price'].mean()
        std = data['price'].std()
        return data[(data['price'] >= mean - std_dev * std) & (data['price'] <= mean + std_dev * std)]
    return data

# Callback to update dropdown options dynamically
@app.callback(
    [
        Output('make-dropdown', 'options'),
        Output('year-dropdown', 'options'),
        Output('location-dropdown', 'options')
    ],
    [Input('model-dropdown', 'value')]
)
def update_dropdowns(selected_model):
    filtered_df = df if not selected_model else df[df['model'].isin(selected_model)]
    makes = [{'label': make, 'value': make} for make in filtered_df['make'].unique()]
    years = [{'label': year, 'value': year} for year in sorted(filtered_df['year'].unique())]
    locations = [{'label': loc, 'value': loc} for loc in filtered_df['location'].unique()]
    return makes, years, locations

# Callback to update the graph and regression info
@app.callback(
    [Output('scatter-plot', 'figure'), Output('regression-info', 'children')],
    [
        Input('make-dropdown', 'value'),
        Input('model-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('location-dropdown', 'value'),
        Input('outlier-exclusion', 'value'),
        Input('std-dev-input', 'value'),
        Input('regression-checkbox', 'value')
    ]
)
def update_graph(selected_make, selected_model, selected_year, selected_location, outlier_option, std_dev, regression_option):
    # Filter the data based on user selections
    filtered_df = df.copy()
    if selected_make:
        filtered_df = filtered_df[filtered_df['make'].isin(selected_make)]
    if selected_model:
        filtered_df = filtered_df[filtered_df['model'].isin(selected_model)]
    if selected_year:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_year)]
    if selected_location:
        filtered_df = filtered_df[filtered_df['location'].isin(selected_location)]

    # Apply outlier exclusion
    filtered_df = filter_outliers(filtered_df, outlier_option, std_dev)

    if filtered_df.empty:
        return go.Figure(data=[], layout=go.Layout(title="No Data Available")), "No data available."

    # Create scatter plot
    fig = px.scatter(filtered_df, x='log_odometer', y='price',
                     labels={'log_odometer': 'Log of Odometer', 'price': 'Price'},
                     title='Price vs. Log of Mileage')

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)')
    )

    regression_table = html.Table([
        html.Tr([html.Th("Metric"), html.Th("Value")]),
        html.Tr([html.Td("Equation"), html.Td("Not Available")])
    ])

    if 'regression' in regression_option:
        X = sm.add_constant(filtered_df['log_odometer'])
        model = sm.OLS(filtered_df['price'], X).fit()
        equation = " + ".join([f"{coef:.2f}*{name}" for name, coef in model.params.items() if name != 'const'])

        regression_table = html.Table([
            html.Tr([html.Th("Metric"), html.Th("Value")]),
            html.Tr([html.Td("Equation"), html.Td(f"y = {equation}")]),
            html.Tr([html.Td("Sample Size"), html.Td(len(filtered_df))]),
            html.Tr([html.Td("R²"), html.Td(f"{model.rsquared:.2f}")]),
            html.Tr([html.Td("Adjusted R²"), html.Td(f"{model.rsquared_adj:.2f}")])
        ])

    return fig, regression_table

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
