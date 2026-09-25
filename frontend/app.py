
import os
import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend.
# Inside the Docker network the backend container is reachable by its service name.
# Override with the BACKEND_URL environment variable to point at any other host.
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon=":shopping_cart:", layout="centered")

# Page title
st.title("SuperKart Sales Prediction System")
st.write("Enter the product and store details below to predict the total sales for that product in that store.")
st.caption(f"Backend: {BACKEND_URL}")

# Input fields for product and store data
col1, col2 = st.columns(2)

with col1:
    st.subheader("Product")
    Product_Weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66)
    Product_Sugar_Content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    Product_Allocated_Area = st.number_input("Product Allocated Area", min_value=0.0, max_value=1.0, value=0.027, format="%.3f")
    Product_MRP = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08)
    Product_Id_char = st.selectbox("Product ID Prefix", ["FD", "DR", "NC"],
                                   help="FD = Food, DR = Drinks, NC = Non-Consumable")
    Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

with col2:
    st.subheader("Store")
    Store_Size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    Store_Location_City_Type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    Store_Type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2",
                                             "Departmental Store", "Food Mart"])
    Store_Age_Years = st.number_input("Store Age (Years)", min_value=0, max_value=100, value=16)

# Create JSON payload
product_data = {
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Product_Id_char": Product_Id_char,
    "Store_Age_Years": Store_Age_Years,
    "Product_Type_Category": Product_Type_Category,
}

# ---------------- Single (online) prediction ----------------
if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=product_data, timeout=30)
        if response.status_code == 200:
            predicted_sales = response.json()["Sales"]
            st.success(f"Predicted Product Store Sales Total: {predicted_sales:,.2f}")
        else:
            st.error(f"API returned {response.status_code}: {response.text}")
    except Exception as exc:
        st.error(f"Unable to connect to the prediction API: {exc}")

# ---------------- Batch prediction ----------------
st.divider()
st.subheader("Batch Prediction")
st.write("Upload a CSV with one row per product-store combination. "
         "Required columns: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, "
         "Product_MRP, Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, "
         "Store_Age_Years, Product_Type_Category.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    preview = pd.read_csv(uploaded_file)
    st.write("Preview of uploaded data:")
    st.dataframe(preview.head(), use_container_width=True)
    uploaded_file.seek(0)

    if st.button("Predict for Batch", type="primary"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": uploaded_file},
                timeout=120,
            )
        except Exception as exc:
            st.error(f"Unable to connect to the prediction API: {exc}")
            response = None

        if response is not None and response.status_code == 200:
            results = response.json()
            st.success("Predictions completed successfully.")

            out = preview.copy()
            out["Predicted_Sales"] = [results[str(i)] for i in range(len(out))]
            st.dataframe(out, use_container_width=True)

            st.download_button(
                "Download predictions as CSV",
                out.to_csv(index=False).encode("utf-8"),
                file_name="superkart_predictions.csv",
                mime="text/csv",
            )
        elif response is not None:
            st.error(f"API returned {response.status_code}: {response.text}")
