from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
import re
from cloud_workflow import CloudWorkflowResult, publication_status

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RECEIPTS_DIR = PROJECT_ROOT / "build" / "cloud_receipts"

def save_publication_receipt(result: CloudWorkflowResult) -> Path:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", result.campaign_id)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    
    path = RECEIPTS_DIR / (
        f"{safe_id}_{timestamp}_{uuid4().hex[:8]}.json"
    )
    
    payload = asdict(result)
    payload["artifact_path"] = str(result.artifact_path)
    payload["publication_status"] = publication_status(result)
    payload["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
    
    with path.open("x", encoding="utf-8") as stream:
        
        json.dump(payload, stream, indent=2, allow_nan=False)
    
    return path