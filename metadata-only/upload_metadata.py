import json
from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork
import traceback




def create_record_from_dict(record_data, uow):
    """Create and publish a single record from a dict."""
    draft = current_rdm_records_service.create(
        system_identity, record_data, uow=uow
    )

    record = current_rdm_records_service.publish(
        system_identity, draft.id, uow=uow
    )

    return record


def upload_records_from_directory():
    """Upload all JSON records from ./records next to this script."""
    
    # 👇 Resolve path relative to this script file
    script_dir = Path(__file__).parent
    records_dir = script_dir / "records"

    if not records_dir.exists() or not records_dir.is_dir():
        raise ValueError(f"'records' directory not found at: {records_dir}")

    json_files = list(records_dir.glob("*.json"))

    if not json_files:
        print("No JSON files found in 'records' directory.")
        return []

    created_records = []

    for json_file in json_files:
        print(f"Processing: {json_file.name}")

        try:
            with open(json_file, "r") as f:
                record_data = json.load(f)

            # Optional: ensure no files block exists
            record_data.setdefault("files", {"enabled": False})

            with UnitOfWork(db.session) as uow:
                record = create_record_from_dict(record_data, uow)
                uow.commit()

            created_records.append(record)
            print(f"✔ Successfully created: {json_file.name}")

        except Exception:
            print(f"\n✖ Failed for {json_file.name}")
            traceback.print_exc()

    return created_records


# Usage
if __name__ == "__main__":
    upload_records_from_directory()