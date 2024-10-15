## ChatGPT example:
## Plotly


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Sample DataFrame
df = px.data.gapminder()

# Initialize the app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Gapminder Dashboard"),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in df['year'].unique()],
        value=2007
    ),
    dcc.Graph(id='bar-chart')
])

# Define the callback to update the chart
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-dropdown', 'value')]
)
def update_chart(selected_year):
    filtered_df = df[df['year'] == selected_year]
    fig = px.bar(filtered_df, x='continent', y='pop', color='continent',
                 title=f'Population by Continent in {selected_year}')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
