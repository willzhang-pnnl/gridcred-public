import json
import traceback
from pathlib import Path

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def sanitize_record(record_data):
    """
    Convert exported Invenio JSON into a minimal valid create payload.
    This removes all system-managed / invalid fields.
    """

    metadata = record_data.get("metadata", {})

    return {
        "metadata": {
            "title": metadata.get("title", "Untitled"),
            "publication_date": (
                metadata.get("publication_date", "2016").split("/")[0]
                if metadata.get("publication_date")
                else "2016"
            ),
            "resource_type": metadata.get("resource_type", {"id": "dataset"}),
            "creators": metadata.get(
                "creators",
                [
                    {
                        "person_or_org": {
                            "type": "organizational",
                            "name": "Unknown"
                        }
                    }
                ],
            ),
            "description": metadata.get("description", "")
        },
        "files": {"enabled": False},
        "access": {
            "record": "public",
            "files": "public"
        }
    }


def create_and_publish(record_data):
    """Create + publish a single record inside a unit of work."""
    with UnitOfWork(db.session) as uow:
        draft = current_rdm_records_service.create(
            system_identity, record_data, uow=uow
        )

        record = current_rdm_records_service.publish(
            system_identity, draft.id, uow=uow
        )

        uow.commit()

    return record


def ingest_all_records():
    """Main entry point: ingest all JSON files in ./records"""

    script_dir = Path(__file__).parent
    records_dir = script_dir / "records"

    if not records_dir.exists():
        raise ValueError(f"Missing records directory: {records_dir}")

    json_files = sorted(records_dir.glob("*.json"))

    if not json_files:
        print("No JSON files found.")
        return []

    results = []

    for json_file in json_files:
        print(f"\n➡ Processing {json_file.name}")

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            cleaned_data = sanitize_record(raw_data)

            record = create_and_publish(cleaned_data)

            results.append(record)
            print(f"✔ Success: {json_file.name}")

        except Exception:
            print(f"✖ Failed: {json_file.name}")
            traceback.print_exc()

    return results


if __name__ == "__main__":
    ingest_all_records()