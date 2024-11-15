# run this from the command line
# streamlit run C:\Users\jakeq\OneDrive\Documents\GitHub\telling_stories_dashboard\final_dash_2.py

# Imports
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import plotly.express as px

# Load the dataset
df = pd.read_excel(r'C:\Users\jakeq\OneDrive\Documents\GitHub\telling_stories_dashboard\data\montana_listings.xlsx')

# Rename problematic column
df = df.rename(columns={'type': 'vehicle_type'})

# Convert price to numeric, removing any non-numeric values
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['odometer'] = pd.to_numeric(df['odometer'], errors='coerce')

# Drop rows with NaN values in price or odometer
df = df.dropna(subset=['price', 'odometer'])

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

# Sidebar Filters
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

# Calculate residuals for the choropleth
filtered_df['predicted_price'] = model.predict(X)
filtered_df['residual'] = filtered_df['price'] - filtered_df['predicted_price']

# Choropleth of Residuals
st.header("Geographic Distribution")

# Additional check for columns' existence to avoid errors
if 'latitude' in filtered_df.columns and 'longitude' in filtered_df.columns:
    # Remove any rows where lat/lon is null
    geo_df = filtered_df.dropna(subset=['latitude', 'longitude'])
    
    fig = px.scatter_mapbox(
        geo_df,
        lat="latitude",
        lon="longitude",
        color="residual",
        size="price",  # Add size variation based on price
        color_continuous_scale="RdBu",
        zoom=4,
        center={"lat": 46.8797, "lon": -110.3626},  # Center of Montana
        mapbox_style="carto-positron",  # Use a free mapbox style
        title="Geographic Distribution of Prices and Residuals",
        hover_data=["make", "model", "year", "price"]  # Add hover information
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
    available_vars,
    max_selections=2
)

# Ensure selection meets the requirement of 1 or 2 variables
if st.button("Run Model"):
    if len(selected_vars) == 0:
        st.error("Please select at least one categorical variable.")
    else:
        # Create design matrix
        X_custom = pd.DataFrame({'log_odometer': np.log1p(filtered_df['odometer'])})
        
        # Add dummy variables for selected categorical variables
        for var in selected_vars:
            # Convert the column to string type to ensure proper dummy creation
            dummies = pd.get_dummies(filtered_df[var].astype(str), prefix=var, drop_first=True)
            X_custom = pd.concat([X_custom, dummies], axis=1)
        
        # Add constant
        X_custom = sm.add_constant(X_custom)
        
        # Ensure all columns are numeric
        X_custom = X_custom.apply(pd.to_numeric, errors='coerce')
        
        # Drop any rows with NaN values
        mask = X_custom.notna().all(axis=1)
        X_custom = X_custom[mask]
        y = filtered_df['price'][mask]
        
        # Fit the model
        try:
            model_custom = sm.OLS(y, X_custom).fit()
            
            # Display model equation and summary statistics
            st.write("**Model Summary:**")
            st.write(f"**R²**: {model_custom.rsquared:.2f}")
            st.write(f"**F-Statistic**: {model_custom.fvalue:.2f}")
            st.write(f"**Number of Observations**: {model_custom.nobs}")
            
            # Display coefficients
            st.write("\n**Coefficients:**")
            for var, coef in model_custom.params.items():
                st.write(f"{var}: {coef:.2f}")
                
        except Exception as e:
            st.error(f"Error fitting model: {str(e)}")

if st.button("Clear"):
    st.experimental_rerun()