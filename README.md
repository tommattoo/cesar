# CESAR: Property Valuation System

CESAR is an end-to-end property valuation system built on French public transaction data.

It takes a property description as input and returns an estimated market value, a confidence range, and flags anomalous estimates.

CESAR provides a REST API, a command-line interface, and a web interface.


## System Overview

The system is structured around four concerns.

Training loads DVF transaction data, trains a quantile regression model, and exports a versioned artifact.

API serves estimates over HTTP with validation, anomaly detection, and model introspection.

UI provides a browser interface with an interactive map of France and a result panel.

Quality includes acceptance tests that run against the live API and an experiment log to track training runs.

## What it does

A user provides four inputs: surface area, number of rooms, department, and property type.

The system returns an estimated value, a confidence range, and an anomaly flag.

`estimated_value_eur` is the median estimate.  
`value_low_eur` and `value_high_eur` define the 10th and 90th percentile range.  
`anomaly_warning` flags cases where the price per m² falls outside a plausible national range.

The UI displays all outputs and highlights the anomaly warning in orange when triggered.

**Example request**
```bash
curl -X POST http://localhost:8000/estimate/ \
  -H "Content-Type: application/json" \
  -d '{"surface_reelle_bati": 50, "nombre_pieces_principales": 3, "code_departement": "75", "type_local": "Appartement"}'

{
  "estimated_value_eur": 504134.92,
  "value_low_eur": 289421.20,
  "value_high_eur": 566213.85,
  "anomaly_warning": null
} 

 ```
  
## Technical decisions

**Quantile regression instead of a point estimate**  
The original model returned one value. The system now uses three `GradientBoostingRegressor` models trained at the 10th, 50th, and 90th percentiles. This produces a range and avoids false precision.

**Anomaly detection based on price per m²**  
The API computes price per m² and compares it to national thresholds. Below 500 €/m² is flagged as low. Above 20,000 €/m² is flagged as high. This uses a simple rule. It stays transparent and easy to adjust.

**Robust data ingestion**  
DVF exports vary in format. Delimiters change. Headers repeat. Some rows miss target values. The training pipeline handles these cases so new CSV files in `data/` load without manual fixes.

**Experiment tracking**  
Each training run is logged in `experiment_runs/runs.csv` with a timestamp, row count, and notes. This file stays local and is excluded from git. It supports quick comparison of runs without external tools.

**API introspection**  
`/health` checks that model files exist before returning ok. `/model_info` returns the contract version and feature names. These endpoints help with deployment and verification.

## Data

Training data comes from DVF, the French public property transaction registry.

The current model uses about 200,000 transactions across four departments: Paris 15th (75), Creuse (23), Lozère (48), and Corse-du-Sud (2A). This covers both dense urban and rural markets.

CSV files are excluded from the repository through `.gitignore`.

To retrain, download CSV files from https://explore.data.gouv.fr/fr/immobilier and place them in `data/`.

## How to run

### Install
```bash
pip install -e .
cd runtime/rating_ui && npm install
```

### Train
Place CSV files in `data/` and run:
```bash
python -m training.scripts.train_from_minimal_csv
```
The script auto-detects separators, cleans malformed rows, trains the model, and logs the run.

### API
```bash
export CESAR_MODEL_PATH=artifact_storage/model_minimal.joblib
export CESAR_CONTRACT_PATH=artifact_storage/contract_minimal.json
uvicorn runtime.prediction_api.app:app --reload --port 8000
```

### UI
```bash
cd runtime/rating_ui && npm run dev
```
Open http://localhost:5173. Click a department on the map or fill the form manually.

### Acceptance tests
```bash
export CESAR_API_URL=http://localhost:8000
cesar acceptance-tests run
```

### CLI
```bash
cesar predict-one run --surface 50 --pieces 3 --departement 75 --type Appartement
```


## API endpoints

| **Endpoint** | **Method** | **Description** |
| `/health` | GET | Returns ok if model files are present |
| `/model_info` | GET | Returns model version and feature names |
| `/estimate/` | POST | Returns estimate, confidence range, anomaly flag |


## Repository layout
```
prediction_contract/   shared request/response schemas and versioned contract
training/              model training, export, and experiment logging
runtime/
  prediction_api/      FastAPI application
  inference/           model loading and prediction logic
  batch_prediction/    CSV in / CSV out
  rating_ui/           browser interface (TypeScript + Leaflet)
model_acceptance_tests/ test cases and runner
cli/                   command-line entrypoints
artifact_storage/      versioned model and contract files (gitignored)
data/                  training CSVs (gitignored)
```

## Acceptance tests

Seven cases covering normal inputs, edge cases, and expected failures:

| **Case** | **Department** | **Type** | **Expected** |
| Paris apartment 50m² 3 rooms | 75 | Appartement | pass |
| House 100m² 5 rooms Rhône | 69 | Maison | pass |
| Paris studio 18m² 1 room | 75 | Appartement | pass |
| Large house rural dept 23 | 23 | Maison | pass |
| Dépendance Gironde 20m² | 33 | Dépendance | pass |
| Corsica 2A 60m² | 2A | Appartement | pass |
| Invalid type_local | 75 | InvalidType | 422 |


## Contributions

**Tommaso Campi and Alessandro Ivashkevich**
Training pipeline, quantile regression model, anomaly detection, API endpoints (`/health`,
`/model_info`, `/estimate/`), acceptance tests, experiment tracking, data ingestion robustness.
Web UI, interactive France department map, confidence interval display, anomaly warning panel.


## Next steps

- **MAE metric in experiment log** — compute Mean Absolute Error on a held-out test set after
  each training run and pass it to `log_run(metrics={"mae": ...})`, making model comparison
  across runs meaningful
- **GitHub Actions CI** — a single workflow file that installs dependencies, starts the API,
  and runs `cesar acceptance-tests run` on every push                                                                     

