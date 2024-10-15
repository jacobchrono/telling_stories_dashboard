# run from cmd line
# streamlit run C:\Users\jakeq\OneDrive\Documents\GitHub\telling_stories_dashboard\scripts\draft.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import statsmodels.api as sm
import os
from pathlib import Path

# Get the directory containing this script
script_dir = Path(__file__).parent

# Construct the path to the dataset
data_path = script_dir.parent / "data" / "montana_listings.xlsx"

# Check if the path exists
if not data_path.exists():
    raise FileNotFoundError(f"The dataset was not found at: {data_path}")
# Set working directory to the script's directory (using relative path)
script_dir = os.path.dirname(os.path.abspath(__file__))  # Current script directory
data_path = os.path.join(script_dir, "data", "montana_listings.xlsx")  # Full path to the dataset

# Load the dataset
data = pd.read_excel(data_path)

# Rename 'type' to avoid conflict with Python's reserved keywords
data = data.rename(columns={'type': 'vehicle_type'})

# Sidebar: Filters that apply to both plots
st.sidebar.header("Filters")
make_filter = st.sidebar.multiselect("Select Make", options=data['make'].unique())
model_filter = st.sidebar.multiselect("Select Model", options=data['model'].unique())
title_filter = st.sidebar.multiselect("Select Title", options=data['title'].unique())
condition_filter = st.sidebar.multiselect("Select Condition", options=data['condition'].unique())
type_filter = st.sidebar.multiselect("Select Vehicle Type", options=data['vehicle_type'].unique())

# Apply filters with error checking
filtered_data = data.copy()
if make_filter:
    filtered_data = filtered_data[filtered_data['make'].isin(make_filter)]
if model_filter:
    filtered_data = filtered_data[filtered_data['model'].isin(model_filter)]
if title_filter:
    filtered_data = filtered_data[filtered_data['title'].isin(title_filter)]
if condition_filter:
    filtered_data = filtered_data[filtered_data['condition'].isin(condition_filter)]
if type_filter:
    filtered_data = filtered_data[filtered_data['vehicle_type'].isin(type_filter)]

if filtered_data.empty:
    st.error("No data available with the selected filters.")
    st.stop()

# 1. Scatter Plot of Price vs Log(Mileage) with OLS Regression Line
st.title("Vehicle Listings Dashboard")

st.subheader("Scatter Plot: Price vs Log(Mileage)")
try:
    fig_scatter = px.scatter(
        filtered_data, 
        x=np.log(filtered_data['odometer'] + 1), 
        y='price', 
        trendline='ols',
        title="Scatter Plot with OLS Regression Line",
        trendline_color_override='blue',
        opacity=0.6
    )
except KeyError as e:
    st.error(f"Missing column in dataset: {e}")
    st.stop()

# OLS Regression Results
try:
    results = px.get_trendline_results(fig_scatter).iloc[0]["px_fit_results"]
    st.write(f"**R²**: {results.rsquared:.2f}")
    st.write(f"**Correlation Coefficient**: {filtered_data['odometer'].corr(filtered_data['price']):.2f}")
    st.write(f"**Number of Observations**: {len(filtered_data)}")
    coef = results.params[1]
    significance = results.pvalues[1] < 0.05
    st.write(f"**Coefficient**: {coef:.2f} (Statistically {'Significant' if significance else 'Insignificant'})")
except Exception as e:
    st.error(f"Error in calculating regression statistics: {e}")

st.plotly_chart(fig_scatter, use_container_width=True)

# 2. Choropleth Map of Residuals
st.subheader("Choropleth Map of Residuals")
try:
    fig_choropleth = px.scatter_geo(
        filtered_data, 
        lat='latitude', 
        lon='longitude', 
        color='residual', 
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Residuals by Location"
    )
    fig_choropleth.update_geos(fitbounds="locations", visible=False)
    fig_choropleth.update_layout(geo=dict(scope='usa'), margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_choropleth, use_container_width=True)
except KeyError as e:
    st.error(f"Missing column for map generation: {e}")

# 3. Custom Regression Model Builder
st.subheader("Custom Regression Model Builder")

# Only categorical variables for this part
categorical_vars = ['make', 'model', 'title', 'paint', 'drive', 'cylinders', 'fuel', 'vehicle_type', 'transmission', 'condition']
selected_vars = st.multiselect(
    "Select Independent Variables",
    options=categorical_vars + ['year', 'odometer']
)

# Run Regression button
if st.button("Run Regression"):
    try:
        # Prepare data for regression
        X = pd.get_dummies(data[selected_vars], drop_first=True)  # Convert categorical variables
        X = sm.add_constant(X)  # Add intercept
        y = data['price']

        # Fit the model
        model = sm.OLS(y, X).fit()
        st.write("### Regression Results")
        st.write(model.summary())

        # Display human-readable equation
        equation = " + ".join([f"{coef:.2f}*{var}" for var, coef in model.params.items()])
        st.write(f"**Price = {equation}**")

    except KeyError as e:
        st.error(f"Error in regression variables: {e}")
    except Exception as e:
        st.error(f"Error in running regression: {e}")

# Clear button
if st.button("Clear"):
    st.experimental_rerun()
