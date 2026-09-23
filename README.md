# SuperKart Sales Prediction

Forecasts `Product_Store_Sales_Total` for a given product in a given store.

**Model:** tuned Random Forest Regressor inside a scikit-learn pipeline (one-hot encoding + estimator),
serialized with joblib.
**Test performance:** R² 0.9262 | RMSE 290.6 | MAE 115.0 | MAPE 5.11%

## Repository layout

```
backend/    app.py  requirements.txt  Dockerfile  superkart_model.joblib   # Flask API, port 7860
frontend/   app.py  requirements.txt  Dockerfile                          # Streamlit UI, port 8501
docker-compose.yml
```

## Run it

```bash
docker compose up --build
```

- Streamlit UI: http://localhost:8501
- API root:     http://localhost:7860

In a GitHub Codespace, set port **7860** (and 8501) to **Public** in the **Ports** tab and use the
forwarded URLs instead of localhost.

## API

### `GET /`
Health check. Returns a welcome string.

### `POST /v1/predict` — online (single) inference

```json
{
  "Product_Weight": 12.66,
  "Product_Sugar_Content": "Low Sugar",
  "Product_Allocated_Area": 0.027,
  "Product_MRP": 117.08,
  "Store_Size": "Medium",
  "Store_Location_City_Type": "Tier 2",
  "Store_Type": "Supermarket Type2",
  "Product_Id_char": "FD",
  "Store_Age_Years": 16,
  "Product_Type_Category": "Non Perishables"
}
```

Response: `{"Sales": 3701.28}`

### `POST /v1/predictbatch` — batch inference

Multipart upload with form field `file` containing a CSV whose columns are the ten fields above.
Response: `{"0": 3701.28, "1": 2544.91, ...}` keyed by row index.

```bash
curl -X POST -F "file=@Batch_Data_SuperKart.csv" http://localhost:7860/v1/predictbatch
```

## Accepted values

| Field | Values |
|---|---|
| Product_Sugar_Content | Low Sugar, Regular, No Sugar |
| Product_Id_char | FD (food), DR (drinks), NC (non-consumable) |
| Product_Type_Category | Perishables, Non Perishables |
| Store_Size | Small, Medium, High |
| Store_Location_City_Type | Tier 1, Tier 2, Tier 3 |
| Store_Type | Supermarket Type1, Supermarket Type2, Departmental Store, Food Mart |

Unseen categories are handled by `OneHotEncoder(handle_unknown="ignore")` rather than raising,
but predictions for them are extrapolations and should be treated as directional.

## Note on versions

`backend/requirements.txt` is generated from the runtime that trained the model, and the Dockerfile
base image matches that Python minor version. If you retrain, regenerate both — a version drift
between training and serving is the most common cause of a joblib load failure.