# run this from the command line
# streamlit run C:\Users\jakeq\OneDrive\Documents\GitHub\telling_stories_dashboard\final_dash.py

# Imports
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import plotly.express as px

# Load the dataset
# Read in the Excel file containing Montana vehicle listings data.
# This dataset is expected to contain columns relevant to vehicle listings.
df = pd.read_excel(r'C:\Users\jakeq\OneDrive\Documents\GitHub\telling_stories_dashboard\data\montana_listings.xlsx')

# Rename problematic column
# Rename the 'type' column to 'vehicle_type' to avoid conflicts with Python keywords.
df = df.rename(columns={'type': 'vehicle_type'})

# Sidebar for outlier exclusion based on price range
st.sidebar.header("Outlier Exclusion")
min_price, max_price = st.sidebar.slider(
    "Select price range", int(df["price"].min()), int(df["price"].max()), (0, 50000)
)
exclude_outliers = st.sidebar.checkbox("Exclude Outliers", value=True)

# Function to exclude outliers based on the IQR method
def remove_outliers(data, column, threshold=1.5):
    """Exclude outliers in a specified column using the IQR method."""
    q1 = data[column].quantile(0.25)
    q3 = data[column].quantile(0.75)
    iqr = q3 - q1
    return data[(data[column] >= q1 - threshold * iqr) & (data[column] <= q3 + threshold * iqr)]

# Check if outliers should be excluded
if exclude_outliers:
    df = remove_outliers(df, "price")

# Filter data based on user-selected price range
filtered_data = df[(df["price"] >= min_price) & (df["price"] <= max_price)]

# Sidebar Filters for other characteristics
st.sidebar.header("Filters")

# Sidebar Filters
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
    scatter_kws={'alpha': 0.5}, 
    line_kws={"color": "red"}
)
ax.set_xlabel("Log(Odometer)")
ax.set_ylabel("Price")
ax.set_title("Scatter Plot with OLS Regression Line")
st.pyplot(fig)

# Regression Analysis Summary
X = sm.add_constant(np.log1p(filtered_df["odometer"]))
model = sm.OLS(filtered_df["price"], X).fit()
coef_significance = model.pvalues.iloc[1] < 0.05 
corr_coef = np.corrcoef(np.log1p(filtered_df["odometer"]), filtered_df["price"])[0, 1]

# print regression summary statistics and correlation
st.markdown(f"**Correlation Coefficient**: {corr_coef:.2f}")
st.markdown(f"**R²**: {model.rsquared:.2f}")
st.markdown(f"**Number of Observations**: {len(filtered_df)}")
st.markdown(f"**Coefficient Interpretation**: A 1% increase in mileage results in a {model.params.iloc[1]:.2f} change in price.")
st.markdown(f"**Statistical Significance at \u03B1 = 0.05**: {'Yes' if coef_significance else 'No'}")
# Choropleth of Residuals
st.header("Choropleth of Residuals")

# Additional check for columns' existence to avoid errors
if 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns:
    fig = px.scatter_geo(
        filtered_df,
        lat="latitude",
        lon="longitude",
        color="residual",
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Geographic Distribution of Price"
    )
    fig.update_geos(
    visible=False,  # Optional: Hide default map controls
    fitbounds=None,  # Turn off auto-zooming
    center={"lat": 46.8797, "lon": -110.3626},  # Approximate center of Montana
    projection_scale=5,  # Adjust to control the zoom level (lower = zoomed out, higher = zoomed in)
    )
    st.plotly_chart(fig)
else:
    st.warning("Geographic data (latitude/longitude) not found in dataset.")

# Custom Regression Model with selected predictors
st.header("Custom Regression Model")

# Allow selection of categorical variables only
available_vars = ['paint', 'drive', 'cylinders', 'fuel', 'transmission', 'condition']
selected_vars = st.multiselect(
    "Select 1 or 2 Categorical Variables for the Custom Model",
    available_vars, max_selections=2
)

# Ensure selection meets the requirement of 1 or 2 variables
if st.button("Run Model"):
    if len(selected_vars) == 0:
        st.error("Please select at least one categorical variable.")
    else:
        # Prepare the design matrix for the regression model
                # Start the design matrix with log(odometer) as a continuous predictor
        X_custom = pd.DataFrame({'log_odometer': np.log1p(filtered_df['odometer'])})
        # add dummies of the catergorical vars
        X_custom = pd.get_dummies(filtered_df[selected_vars], drop_first=True)
        X_custom = sm.add_constant(X_custom)  # Adding constant term for intercept
        
        #
        print(filtered_df.dtypes)
        print(X_custom.dtypes)

        model_custom = sm.OLS(filtered_df["price"], X_custom).fit()

        # Display model equation and summary statistics
        st.write(f"**Equation**: Price = {model_custom.params[0]:.2f} + " +
                 " + ".join([f"{coef:.2f}*{var}" for var, coef in model_custom.params[1:].items()]))
        st.markdown(f"**R²**: {model_custom.rsquared:.2f}")
        st.markdown(f"**F-Statistic**: {model_custom.fvalue:.2f}")
        st.markdown(f"**Number of Observations**: {model_custom.nobs}")

if st.button("Clear"):
    st.experimental_rerun()
