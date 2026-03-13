from typing import Any

import numpy as np

from prediction_contract.request_schema import EstimateRequest
from prediction_contract.response_schema import EstimateResponse
from prediction_contract.contract_version import ContractVersion


# Raising a dedicated exception for invalid features lets the API return 422 and the CLI print a
# clear message instead of a generic traceback. The contract defines the allowed type_local
# categories; we must use the same order for one-hot encoding as in training.
class InvalidFeatureError(Exception):
    pass


def _code_departement_to_numeric(code: str) -> float:
    s = str(code).strip()
    if s == "2A":
        return 20.0
    if s == "2B":
        return 21.0
    try:
        return float(int(s))
    except ValueError:
        return 0.0


def request_to_feature_row(request: EstimateRequest, contract: ContractVersion) -> np.ndarray:
    categories = contract.type_local_categories
    if request.type_local not in categories:
        raise InvalidFeatureError(f"type_local must be one of {categories}, got {request.type_local!r}")

    dept_num = _code_departement_to_numeric(request.code_departement)
    type_one_hot = [1.0 if c == request.type_local else 0.0 for c in categories]

    ordered = [
        float(request.surface_reelle_bati),
        float(request.nombre_pieces_principales),
        dept_num,
        *type_one_hot,
    ]
    return np.array(ordered, dtype=np.float64).reshape(1, -1)


_ANOMALY_LOW_EUR_PER_SQM = 500.0    # below this price/m² is suspiciously cheap
_ANOMALY_HIGH_EUR_PER_SQM = 20_000.0  # above this price/m² is suspiciously expensive


def _anomaly_warning(estimated_value: float, surface: float) -> str | None:
    if surface <= 0:
        return None
    price_per_sqm = estimated_value / surface
    if price_per_sqm < _ANOMALY_LOW_EUR_PER_SQM:
        return "unusually_low"
    if price_per_sqm > _ANOMALY_HIGH_EUR_PER_SQM:
        return "unusually_high"
    return None


def estimate_from_model(models: dict[str, Any], request: EstimateRequest, contract: ContractVersion) -> EstimateResponse:
    X = request_to_feature_row(request, contract)
    value_mid = float(models["mid"].predict(X).flat[0])
    value_low = float(models["low"].predict(X).flat[0])
    value_high = float(models["high"].predict(X).flat[0])
    warning = _anomaly_warning(value_mid, request.surface_reelle_bati)
    return EstimateResponse(
        estimated_value_eur=value_mid,
        value_low_eur=value_low,
        value_high_eur=value_high,
        anomaly_warning=warning,
    )
