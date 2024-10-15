import streamlit as st
import pandas as pd
import plotly.express as px

# Load sample data
df = px.data.gapminder()

# Title of the dashboard
st.title("Gapminder Dashboard")

# Year slider input
year = st.slider(
    "Select Year", 
    min_value=int(df['year'].min()), 
    max_value=int(df['year'].max()), 
    value=2007
)

# Filter data based on selected year
filtered_df = df[df['year'] == year]

# Create the bar chart using Plotly
fig = px.bar(
    filtered_df, 
    x='continent', 
    y='pop', 
    color='continent', 
    title=f'Population by Continent in {year}'
)

# Display the chart
st.plotly_chart(fig)