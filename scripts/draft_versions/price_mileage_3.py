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
        html.Label("Select Make:"),
        dcc.Dropdown(
            id='make-dropdown',
            options=[{'label': make, 'value': make} for make in df['make'].unique()],
            value=None,
            multi=True
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),

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
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in sorted(df['year'].unique())],
            value=None,
            multi=True
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select location:"),
        dcc.Dropdown(
            id='location-dropdown',
            options=[{'label': location, 'value': location} for location in df['location'].unique()],
            value=None,
            multi=True
        ),
    ], style={'width': '20%', 'display': 'inline-block'}),

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

    # Text box for regression equation and interpretation
    html.Div(id='regression-info', style={'marginTop': '30px', 'padding': '20px', 
                                          'border': '1px solid #ccc', 'borderRadius': '5px'})
])

# Callback to update the graph and regression info
@app.callback(
    [Output('scatter-plot', 'figure'), Output('regression-info', 'children')],
    [
        Input('make-dropdown', 'value'),
        Input('model-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('location-dropdown', 'value'),
        Input('regression-checkbox', 'value')
    ]
)
def update_graph(selected_make, selected_model, selected_year, selected_location, regression_option):
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

    # Check if there's data after filtering
    if filtered_df.empty:
        return go.Figure(data=[], layout=go.Layout(title="No Data Available")), "No data available for the selected filters."

    # Create scatter plot
    fig = px.scatter(filtered_df, x='log_odometer', y='price',
                     labels={'log_odometer': 'Log of Odometer', 'price': 'Price'},
                     title='Price vs. Log of Mileage')

    # Adjust transparency of gridlines and background
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)')
    )

    regression_info = "Regression line not shown."
    
    if 'regression' in regression_option:
        # Add dummy variables if make or location filters are applied
        X = sm.add_constant(filtered_df['log_odometer'])
        if selected_make:
            make_dummies = pd.get_dummies(filtered_df['make'], drop_first=True)
            X = pd.concat([X, make_dummies], axis=1)
        if selected_location:
            location_dummies = pd.get_dummies(filtered_df['location'], drop_first=True)
            X = pd.concat([X, location_dummies], axis=1)

        model = sm.OLS(filtered_df['price'], X).fit()
        predictions = model.predict(X)

        # Add regression line to the scatter plot
        fig.add_trace(
            go.Scatter(x=filtered_df['log_odometer'], y=predictions,
                       mode='lines', name='Regression Line')
        )

        # Build regression equation and statistics
        equation = " + ".join([f"{coef:.2f}*{name}" for name, coef in model.params.items() if name != 'const'])
        r_squared = model.rsquared
        adj_r_squared = model.rsquared_adj
        sample_size = len(filtered_df)

        regression_info = (
            f"**Regression Equation:** y = {equation}\n\n"
            f"**Sample Size:** {sample_size}\n\n"
            f"**R²:** {r_squared:.2f}\n\n"
            f"**Adjusted R²:** {adj_r_squared:.2f}\n\n"
            "**Interpretation:** A 1% increase in mileage corresponds to a "
            f"{model.params['log_odometer']:.2f} change in price."
        )

    return fig, regression_info

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
