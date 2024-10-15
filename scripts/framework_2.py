# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Cache the data to prevent reloading on every run
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_excel(file_path)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Load the dataset
file_path = "data/montana_listings.xlsx"  # Adjust this path if needed
data = load_data(file_path)

# Error handling if data is not loaded correctly
if data is None:
    st.stop()

# Sidebar for filters and outlier exclusion
st.sidebar.header("Filters and Options")
min_price, max_price = st.sidebar.slider(
    "Select price range", int(data["price"].min()), int(data["price"].max()), (0, 50000)
)
exclude_outliers = st.sidebar.checkbox("Exclude Outliers", value=True)

# Function to exclude outliers based on price
def remove_outliers(df, column, threshold=1.5):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    return df[(df[column] >= q1 - threshold * iqr) & (df[column] <= q3 + threshold * iqr)]

if exclude_outliers:
    data = remove_outliers(data, "price")

filtered_data = data[(data["price"] >= min_price) & (data["price"] <= max_price)]

# Scatter plot: Price vs. Log of Odometer
st.header("Scatter Plot: Price vs. Log(Odometer)")
filtered_data["log_odometer"] = np.log1p(filtered_data["odometer"])  # Log transformation
fig_scatter = px.scatter(
    filtered_data, x="log_odometer", y="price", title="Price vs Log(Odometer)",
    labels={"log_odometer": "Log(Odometer)", "price": "Price"}
)
st.plotly_chart(fig_scatter)

# Choropleth Map: Residuals by Latitude and Longitude
st.header("Choropleth Map: Residuals")
X = filtered_data[["odometer"]]
y = filtered_data["price"]
model = LinearRegression().fit(X, y)
filtered_data["predicted_price"] = model.predict(X)
filtered_data["residual"] = filtered_data["price"] - filtered_data["predicted_price"]

fig_choropleth = px.density_mapbox(
    filtered_data, lat="latitude", lon="longitude", z="residual", radius=10,
    center=dict(lat=46.8797, lon=-110.3626), zoom=6,
    mapbox_style="carto-positron", title="Residuals by Latitude and Longitude"
)
st.plotly_chart(fig_choropleth)

# Custom Regression Section
st.header("Custom Regression Model")
st.write("Use this section to create and explore custom regression models on the dataset.")

target_column = st.selectbox("Select Target Column", data.columns)
feature_columns = st.multiselect("Select Feature Columns", [col for col in data.columns if col != target_column])

if st.button("Train Model"):
    if not feature_columns:
        st.error("Please select at least one feature column.")
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            data[feature_columns], data[target_column], test_size=0.3, random_state=42
        )
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        st.success(f"Model trained! Mean Squared Error: {mse:.2f}")

        # Show predictions and residuals
        results = pd.DataFrame({"Actual": y_test, "Predicted": y_pred, "Residual": y_test - y_pred})
        st.write(results)

# Instructions and placeholders for future features
st.sidebar.write("---")
st.sidebar.write("## Future Enhancements")
st.sidebar.write(
    """
    - Add additional filtering options (e.g., based on location or date).
    - Implement interactive elements (e.g., sliders for model hyperparameters).
    - Explore additional regression models (e.g., Ridge, Lasso).
    """
)
