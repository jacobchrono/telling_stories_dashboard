

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from io import BytesIO

# Cache the data to load only once
@st.cache_data
def load_data():
    data_path = "data/montana_listings.xlsx"
    return pd.read_excel(data_path)

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
price_range = st.sidebar.slider("Select Price Range", int(df['price'].min()), int(df['price'].max()), (500, 10000))
exclude_outliers = st.sidebar.checkbox("Exclude Outliers", value=True)

# Optional: Outlier exclusion logic (modify as needed)
if exclude_outliers:
    df = df[(df['price'] < df['price'].quantile(0.95))]

# --- Scatter Plot: Price vs Log(Odometer) with OLS Regression ---
st.header("Price vs Log(Odometer)")
df['log_odometer'] = np.log(df['odometer'])

fig, ax = plt.subplots()
ax.scatter(df['log_odometer'], df['price'], alpha=0.6)
ax.set_xlabel('Log(Odometer)')
ax.set_ylabel('Price')

# Perform OLS regression
X = sm.add_constant(df['log_odometer'])  # Add intercept
ols_model = sm.OLS(df['price'], X).fit()
df['fitted'] = ols_model.predict(X)

# Plot regression line
ax.plot(df['log_odometer'], df['fitted'], color='red', linewidth=2)

# Display OLS statistics in a table
st.write("**OLS Regression Results:**")
st.table({
    'R^2': [ols_model.rsquared],
    'Correlation Coefficient': [df[['log_odometer', 'price']].corr().iloc[0, 1]],
    'Observations': [len(df)],
    'Coefficient Interpretation': ["For each unit increase in log(odometer), the price changes by the coefficient."],
    'Significance': [ols_model.pvalues[1] < 0.05]
})

st.pyplot(fig)

# --- Choropleth Map of Residuals ---
st.header("Choropleth Map of Residuals by Latitude and Longitude")
df['residuals'] = df['price'] - df['fitted']

fig_map = px.scatter_mapbox(
    df, lat='latitude', lon='longitude', color='residuals',
    color_continuous_scale=px.colors.cyclical.IceFire,
    mapbox_style="carto-positron", zoom=5, center={"lat": 47.0, "lon": -110.0},
    title="Residuals by Location"
)
st.plotly_chart(fig_map)

# --- Custom Regression Model Section ---
st.header("Custom Regression Model")

with st.form("regression_form"):
    predictors = st.multiselect("Select Predictors", df.columns, default=['log_odometer'])
    submit_button = st.form_submit_button("Run Regression")
    clear_button = st.form_submit_button("Clear")

if submit_button and predictors:
    X_custom = sm.add_constant(df[predictors])
    custom_model = sm.OLS(df['price'], X_custom).fit()
    
    st.write(f"**Regression Equation:** price = {custom_model.params[0]:.2f} + "
             + " + ".join([f"{coef:.2f}*{name}" for name, coef in custom_model.params.items()][1:]))
    
    st.table({
        'R^2': [custom_model.rsquared],
        'F-statistic': [custom_model.fvalue],
        'Observations': [custom_model.nobs]
    })
