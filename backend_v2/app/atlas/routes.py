from fastapi import APIRouter, HTTPException
import json
import requests
from pathlib import Path

router = APIRouter(prefix="/atlas", tags=["MissionAtlas"])


@router.get("/lineage/client/{client_id}/concept/{concept_id}")
def get_lineage_with_value(client_id: int, concept_id: str):
    # 1. Load lineage artefact (repo-root anchored path)
    BASE_DIR = Path(__file__).resolve().parents[3]  # scv-repo root
    artefact_path = (
        BASE_DIR
        / "evidence"
        / "lineage"
        / f"client_{client_id}__{concept_id}.json"
    )

    try:
        with open(artefact_path, "r") as f:
            artefact = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Lineage artefact not found")

    # 2. Resolve live value
    value_ref = artefact["value_reference"]
    endpoint = value_ref["endpoint"]
    json_path = value_ref["json_path"]

    try:
        response = requests.get(f"http://127.0.0.1:8000{endpoint}")
        response.raise_for_status()
        payload = response.json()
    except Exception as e:
        return {
            "artifact": artefact,
            "resolved_value": None,
            "resolution": {
                "status": "error",
                "details": str(e),
            },
        }

    # 3. Extract value (handles dict or list payload)
    field_name = json_path.replace("$.", "")

    resolved_value = None
    if isinstance(payload, dict):
        resolved_value = payload.get(field_name)
    elif isinstance(payload, list):
        record = next(
            (x for x in payload if isinstance(x, dict) and x.get("id") == client_id),
            None,
        )
        if record:
            resolved_value = record.get(field_name)

    return {
        "artifact": artefact,
        "resolved_value": resolved_value,
        "resolution": {
            "status": "ok" if resolved_value is not None else "not_found",
            "details": f"Resolved from {endpoint} at {json_path}",
        },
    }

