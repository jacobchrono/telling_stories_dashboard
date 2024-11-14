# run this from the cmd line
# streamlit run C:\Users\jakeq\OneDrive\Documents\GitHub\telling_stories_dashboard\scripts\final_dash.py

# imports
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import plotly.express as px
import os

# Load the dataset
df = pd.read_excel(r'C:\Users\jakeq\OneDrive\Documents\GitHub\telling_stories_dashboard\data\montana_listings.xlsx')

# Rename problematic column
df = df.rename(columns={'type': 'vehicle_type'})

# Sidebar Filters
st.sidebar.header("Filters")
make_filter = st.sidebar.multiselect("Make", df["make"].unique())
model_filter = st.sidebar.multiselect("Model", df["model"].unique())
title_filter = st.sidebar.multiselect("Title", df["title"].unique())
condition_filter = st.sidebar.multiselect("Condition", df["condition"].unique())
vehicle_type_filter = st.sidebar.multiselect("Vehicle Type", df["vehicle_type"].unique())

# Year filter using a range slider
min_year = int(df["year"].min())
max_year = int(df["year"].max())
year_filter = st.sidebar.slider("Year", min_year, max_year, (min_year, max_year))

# Apply filters
filtered_df = df[
    (df["make"].isin(make_filter) if make_filter else pd.Series([True] * len(df))) &
    (df["model"].isin(model_filter) if model_filter else pd.Series([True] * len(df))) &
    (df["title"].isin(title_filter) if title_filter else pd.Series([True] * len(df))) &
    (df["condition"].isin(condition_filter) if condition_filter else pd.Series([True] * len(df))) &
    (df["vehicle_type"].isin(vehicle_type_filter) if vehicle_type_filter else pd.Series([True] * len(df))) &
    (df["year"].between(year_filter[0], year_filter[1]))
]

# Scatter plot of price vs log(mileage)
st.header("Price vs Log(Mileage) with Regression Line")

fig, ax = plt.subplots()
sns.regplot(
    x=np.log1p(filtered_df["odometer"]), 
    y=filtered_df["price"], 
    ax=ax, 
    scatter_kws={'alpha':0.5}, 
    line_kws={"color": "red"}
)
ax.set_xlabel("Log(Odometer)")
ax.set_ylabel("Price")
ax.set_title("Scatter Plot with OLS Regression Line")
ax.set_facecolor('none')

# Regression Analysis Summary
X = sm.add_constant(np.log1p(filtered_df["odometer"]))
model = sm.OLS(filtered_df["price"], X).fit()
r_squared = model.rsquared
corr_coef = np.corrcoef(np.log1p(filtered_df["odometer"]), filtered_df["price"])[0, 1]
num_observations = len(filtered_df)
coef_significance = model.pvalues.iloc[1] < 0.05

st.pyplot(fig)
st.markdown(f"**R²**: {r_squared:.2f}")
st.markdown(f"**Correlation Coefficient**: {corr_coef:.2f}")
st.markdown(f"**Number of Observations**: {num_observations}")
st.markdown(f"**Coefficient Interpretation**: A 1% increase in mileage results in a {model.params.iloc[1]:.2f} change in price.")
st.markdown(f"**Statistical Significance**: {'Yes' if coef_significance else 'No'}")

# Choropleth of Residuals
st.header("Choropleth of Residuals")

fig = px.scatter_geo(
    filtered_df,
    lat="latitude",
    lon="longitude",
    color="residual",
    color_continuous_scale=px.colors.sequential.Viridis,
    title="Geographic Distribution of Residuals",
)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(geo=dict(projection_scale=3, center={"lat": 46.8797, "lon": -110.3626}))

st.plotly_chart(fig)

# Custom Regression Model
st.header("Custom Regression Model")

variables = st.multiselect("Select Variables", df.columns.drop(["price", "residual"]))
if st.button("Run Model"):
    X_custom = pd.get_dummies(filtered_df[variables], drop_first=True)
    X_custom = sm.add_constant(X_custom)
    model_custom = sm.OLS(filtered_df["price"], X_custom).fit()

    st.write(f"**Equation**: Price = {model_custom.params[0]:.2f} + " +
             " + ".join([f"{coef:.2f}*{var}" for var, coef in model_custom.params[1:].items()]))
    st.markdown(f"**R²**: {model_custom.rsquared:.2f}")
    st.markdown(f"**F-Statistic**: {model_custom.fvalue:.2f}")
    st.markdown(f"**Number of Observations**: {model_custom.nobs}")

if st.button("Clear"):
    st.experimental_rerun()
