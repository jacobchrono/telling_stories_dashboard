'''
How to Run the Dashboard
1. Save the code in a file named dashboard.py.

2. Open the terminal and navigate to the directory where the file is saved.

3. Run the following command:
bash
Copy code
python dashboard.py

4.Open the displayed URL in your browser (usually http://127.0.0.1:8050).

'''


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
df = df[['make', 'model', 'year', 'odometer', 'price']].dropna()
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

    # Dropdowns for make, model, and year filters
    html.Div([
        html.Label("Select Make:"),
        dcc.Dropdown(
            id='make-dropdown',
            options=[{'label': make, 'value': make} for make in df['make'].unique()],
            value=None,
            multi=True
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Model:"),
        dcc.Dropdown(
            id='model-dropdown',
            options=[{'label': model, 'value': model} for model in df['model'].unique()],
            value=None,
            multi=True
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in sorted(df['year'].unique())],
            value=None,
            multi=True
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),

    # Checkbox to add regression line
    html.Div([
        dcc.Checklist(
            id='regression-checkbox',
            options=[{'label': 'Show Regression Line', 'value': 'regression'}],
            value=[]
        ),
    ], style={'textAlign': 'center', 'marginTop': '20px'}),

    # Graph to display results
    dcc.Graph(id='scatter-plot')
])

# Callback to update the scatter plot based on filters and checkbox
@app.callback(
    Output('scatter-plot', 'figure'),
    [
        Input('make-dropdown', 'value'),
        Input('model-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('regression-checkbox', 'value')
    ]
)
def update_graph(selected_make, selected_model, selected_year, regression_option):
    # Filter the data based on user selections
    filtered_df = df.copy()
    if selected_make:
        filtered_df = filtered_df[filtered_df['make'].isin(selected_make)]
    if selected_model:
        filtered_df = filtered_df[filtered_df['model'].isin(selected_model)]
    if selected_year:
        filtered_df = filtered_df[filtered_df['year'].isin(selected_year)]

    # Check if there's data after filtering
    if filtered_df.empty:
        return go.Figure(data=[], layout=go.Layout(title="No Data Available"))

    # Create scatter plot
    fig = px.scatter(filtered_df, x='log_odometer', y='price',
                     labels={'log_odometer': 'Log of Odometer', 'price': 'Price'},
                     title='Price vs. Log of Mileage')

    # Add regression line if selected
    if 'regression' in regression_option:
        X = sm.add_constant(filtered_df['log_odometer'])
        model = sm.OLS(filtered_df['price'], X).fit()
        predictions = model.predict(X)

        # Add regression line to the scatter plot
        fig.add_trace(
            go.Scatter(x=filtered_df['log_odometer'], y=predictions,
                       mode='lines', name='Regression Line')
        )

        # Add equation and R-squared to the plot
        intercept, slope = model.params
        r_squared = model.rsquared
        equation = f"y = {intercept:.2f} + {slope:.2f} * x<br>R² = {r_squared:.2f}"
        fig.add_annotation(
            x=0.05, y=0.95, xref="paper", yref="paper",
            text=equation, showarrow=False, align="left"
        )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
