# Import necessary libraries
import numpy as np
import joblib                                  # For loading the serialized model
from pathlib import Path                       # So the model path does not depend on cwd
import pandas as pd                            # For data manipulation
from flask import Flask, request, jsonify      # For creating the Flask API

# Initialize Flask app with a name
superkart_api = Flask("SuperKart")

# Cap uploads at 10 MB. Without this an arbitrarily large POST is read into memory.
superkart_api.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Load the trained model (full pipeline: OneHotEncoder + tuned Random Forest).
# Resolved relative to THIS file, so the API also starts when launched from another directory.
MODEL_PATH = Path(__file__).parent / "superkart_model.joblib"
model = joblib.load(MODEL_PATH)

# The exact feature set the pipeline was trained on, in order.
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Home / health route
@superkart_api.get('/')
def home():
    return "Welcome to the SuperKart Sales Prediction API"


# Endpoint to predict sales for a single product
@superkart_api.post('/v1/predict')
def predict_sales():
    # Get JSON data from the request
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Request body must be JSON'}), 400
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object, not a list'}), 400

    # Reject incomplete payloads explicitly rather than failing deep inside the pipeline
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

    # Extract the model features from the input data
    sample = {f: data[f] for f in FEATURES}

    # Convert the extracted data into a DataFrame
    input_data = pd.DataFrame([sample])

    # Make a prediction using the trained model
    try:
        prediction = model.predict(input_data).tolist()[0]
    except Exception as exc:
        return jsonify({'error': f'Prediction failed: {exc}'}), 400

    # Return the prediction as a JSON response
    return jsonify({'Sales': round(prediction, 2)})


# Endpoint to predict sales for a batch of products
@superkart_api.post('/v1/predictbatch')
def predict_sales_batch():
    # Get the uploaded CSV file from the request
    file = request.files.get('file')
    if file is None:
        return jsonify({'error': "No file part named 'file' in the request"}), 400

    # Read the file into a DataFrame
    try:
        input_data = pd.read_csv(file)
    except Exception as exc:
        return jsonify({'error': f'Could not parse CSV: {exc}'}), 400

    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({'error': 'CSV is missing required columns', 'missing': missing}), 400

    # Make predictions for the batch data. Bad cell values (text in a numeric column,
    # an empty frame) must surface as a clean 400 rather than a 500.
    try:
        predictions = model.predict(input_data[FEATURES]).tolist()
    except Exception as exc:
        return jsonify({'error': f'Prediction failed: {exc}'}), 400

    # Create an output dictionary mapping row index to predicted sales
    output_dict = {str(i): round(pred, 2) for i, pred in enumerate(predictions)}

    return output_dict


# Run the Flask app (development only -- production uses Gunicorn, see the Dockerfile)
if __name__ == '__main__':
    # debug must stay False: the Werkzeug debugger is remote code execution behind a
    # guessable PIN, and this binds to every interface.
    superkart_api.run(host='0.0.0.0', port=7860, debug=False)