
import streamlit as st
import requests
import pandas as pd
import numpy as np
import json

# Assuming your Flask API is running on this URL
# For local testing, you might use 'http://localhost:7860'
# For Codespaces, you will use the forwarded URL for port 7860
FLASK_API_ROOT_URL = 'http://backend:7860' # 'backend' is the service name in docker-compose

st.set_page_config(layout="wide")

st.title('SuperKart Sales Prediction App')

st.markdown("""
This application predicts the `Product_Store_Sales_Total` based on various product and store features.
It interacts with a Flask API that hosts the trained machine learning model.
""")

st.sidebar.header('Input Features')

# Input fields for online prediction
product_id = st.sidebar.text_input('Product ID (e.g., FD6114)', 'FD6114')
product_weight = st.sidebar.number_input('Product Weight (kg)', min_value=0.1, max_value=50.0, value=12.66, step=0.1)
product_sugar_content = st.sidebar.selectbox('Product Sugar Content', ['Low Sugar', 'Regular', 'No Sugar'])
product_allocated_area = st.sidebar.number_input('Product Allocated Area Ratio', min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f")
product_type = st.sidebar.selectbox('Product Type',
                                    ['Frozen Foods', 'Dairy', 'Canned', 'Baking Goods', 'Health and Hygiene', 'Snack Foods', 'Soft Drinks', 'Meat', 'Fruits and Vegetables', 'Hard Drinks', 'Breakfast', 'Household', 'Seafood', 'Starchy Foods', 'Others', 'Bread'])
product_mrp = st.sidebar.number_input('Product MRP', min_value=10.0, max_value=300.0, value=117.08, step=1.0)
store_id = st.sidebar.selectbox('Store ID', ['OUT004', 'OUT003', 'OUT001', 'OUT002', 'OUT005', 'OUT006', 'OUT007', 'OUT008', 'OUT009', 'OUT010'])
store_establishment_year = st.sidebar.number_input('Store Establishment Year', min_value=1950, max_value=2023, value=2009, step=1)
store_size = st.sidebar.selectbox('Store Size', ['Medium', 'High', 'Small'])
store_location_city_type = st.sidebar.selectbox('Store Location City Type', ['Tier 2', 'Tier 1', 'Tier 3'])
store_type = st.sidebar.selectbox('Store Type', ['Supermarket Type2', 'Departmental Store', 'Supermarket Type1', 'Food Mart'])


# Function to create payload for Flask API
def create_payload(product_id, product_weight, product_sugar_content, product_allocated_area, product_type, product_mrp, store_id, store_establishment_year, store_size, store_location_city_type, store_type):
    # Replicate feature engineering steps performed in the notebook
    product_id_char = product_id[:2]
    current_year = 2024 # Assuming 2024 as current year for Store_Age_Years calculation
    store_age_years = current_year - store_establishment_year

    product_type_map = {
        'Dairy': 'Perishable',
        'Meat': 'Perishable',
        'Fruits and Vegetables': 'Perishable',
        'Frozen Foods': 'Perishable',
        'Seafood': 'Perishable',
        'Snack Foods': 'Non Perishable',
        'Baking Goods': 'Non Perishable',
        'Canned': 'Non Perishable',
        'Bread': 'Non Perishable',
        'Breakfast': 'Non Perishable',
        'Starchy Foods': 'Non Perishable',
        'Health and Hygiene': 'Non Perishable',
        'Household': 'Non Perishable',
        'Others': 'Non Perishable',
        'Soft Drinks': 'Drinks',
        'Hard Drinks': 'Drinks'
    }
    product_type_category = product_type_map.get(product_type, 'Non Perishable') # Fallback as in notebook

    payload = {
        'Product_Id': product_id, # Keep for feature engineering in Flask app
        'Product_Weight': product_weight,
        'Product_Sugar_Content': product_sugar_content,
        'Product_Allocated_Area': product_allocated_area,
        'Product_Type': product_type, # Keep for feature engineering in Flask app
        'Product_MRP': product_mrp,
        'Store_Id': store_id,
        'Store_Establishment_Year': store_establishment_year, # Keep for feature engineering in Flask app
        'Store_Size': store_size,
        'Store_Location_City_Type': store_location_city_type,
        'Store_Type': store_type,
        'Product_Id_char': product_id_char, # Directly engineered, but Flask also uses it
        'Store_Age_Years': store_age_years, # Directly engineered, but Flask also uses it
        'Product_Type_Category': product_type_category # Directly engineered, but Flask also uses it
    }
    return payload

# Main area for online prediction
st.subheader('Online Prediction (Single Instance)')
if st.button('Predict Sales for Single Product'):
    online_payload = create_payload(
        product_id, product_weight, product_sugar_content, product_allocated_area, product_type,
        product_mrp, store_id, store_establishment_year, store_size, store_location_city_type, store_type
    )
    try:
        response = requests.post(f'{FLASK_API_ROOT_URL}/v1/predict', json=online_payload)
        if response.status_code == 200:
            prediction = response.json().get('prediction')[0]
            st.success(f'Predicted Sales Total: **${prediction:,.2f}**')
        else:
            st.error(f'Error from API: {response.status_code} - {response.text}')
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to Flask API at {FLASK_API_ROOT_URL}. Make sure the backend service is running and accessible.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Main area for batch prediction
st.subheader('Batch Prediction (Upload CSV)')
uploaded_file = st.file_uploader("Upload a CSV file for batch prediction", type=["csv"])

if uploaded_file is not None:
    batch_df = pd.read_csv(uploaded_file)
    st.write('Uploaded Data Preview:')
    st.dataframe(batch_df.head())

    if st.button('Predict Sales for Batch Data'):
        try:
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/csv')}
            response = requests.post(f'{FLASK_API_ROOT_URL}/v1/predictbatch', files=files)

            if response.status_code == 200:
                predictions = response.json()
                predictions_df = pd.DataFrame(list(predictions.items()), columns=['Index', 'Predicted_Sales'])
                predictions_df['Index'] = predictions_df['Index'].astype(int)
                predictions_df = predictions_df.set_index('Index')
                st.success('Batch predictions successful!')
                st.write('Predicted Sales for Batch Data:')
                st.dataframe(predictions_df)

                # Optionally, allow downloading predictions
                csv_output = predictions_df.to_csv().encode('utf-8')
                st.download_button(
                    label="Download Predictions as CSV",
                    data=csv_output,
                    file_name='batch_predictions.csv',
                    mime='text/csv',
                )
            else:
                st.error(f'Error from API: {response.status_code} - {response.text}')
        except requests.exceptions.ConnectionError:
            st.error(f"Could not connect to Flask API at {FLASK_API_ROOT_URL}. Make sure the backend service is running and accessible.")
        except Exception as e:
            st.error(f"An unexpected error occurred during batch prediction: {e}")
