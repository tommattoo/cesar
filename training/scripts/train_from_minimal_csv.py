"""
Train the model using all CSV files in the data/ folder.

- Finds every *.csv in data/
- Checks that each file has the required columns (surface, rooms, department, type, value)
- Checks that all files have the same columns (same schema); if not, raises an error
- Combines all rows and trains one model
- Saves the model and contract to artifact_storage/

Run from repo root: python -m training.scripts.train_from_minimal_csv
"""

from pathlib import Path

from training.asset_rating_model.train_and_export import (
    load_all_csvs_from_dir,
    train_on_dataframe,
    export_artifact,
)

from training.experiment_log import log_run

# Where to find data and where to write the model (relative to repo root).
DATA_DIR_NAME = "data"
ARTIFACT_DIR_NAME = "artifact_storage"


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    data_dir = repo_root / DATA_DIR_NAME
    artifact_dir = repo_root / ARTIFACT_DIR_NAME

    # Load and validate: all CSVs in data/ must have the same columns and the required ones.
    print(f"Loading CSVs from {data_dir} ...")
    combined = load_all_csvs_from_dir(data_dir, separator=";")
    num_rows = len(combined)
    num_files = len(list(data_dir.glob("*.csv")))
    print(f"  Found {num_files} file(s), {num_rows} rows in total.")

    # Train one model on the combined data.
    print("Training model ...")
    model, mae = train_on_dataframe(combined)

    model_path, contract_path = export_artifact(
        model,
        artifact_dir,
        model_version="minimal",
    )
    print(f"  Model:    {model_path}")
    print(f"  Contract: {contract_path}")
    print(f"  MAE: {mae:,.0f} €")
    version = model_path.stem.replace("model_", "")
    log_run(version, train_rows=num_rows, notes=f"{num_files} CSV file(s) from data/", metrics={"mae": round(mae)})
    print(f"  Run logged to experiment_runs/runs.csv")

    print(
        "Set CESAR_MODEL_PATH and CESAR_CONTRACT_PATH to these paths "
        "(or symlink as model_latest.joblib / contract_latest.json)."
    )


if __name__ == "__main__":
    main()
