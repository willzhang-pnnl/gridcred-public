import json
from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def sanitize_record(data: dict) -> dict:
    """Remove system-managed fields that break Invenio validation."""

    data.pop("status", None)
    data.pop("is_draft", None)
    data.pop("created", None)
    data.pop("updated", None)
    data.pop("revision_id", None)
    data.pop("id", None)
    data.pop("parent", None)
    data.pop("versions", None)

    return data


def create_record_from_file(filename="record-zen.json"):
    """Create and publish a record by reading JSON from a file."""

    script_dir = Path(__file__).parent
    record_file = script_dir / filename

    with open(record_file, "r") as f:
        record_data = json.load(f)

    # 🔥 FIX: sanitize input before sending to Invenio
    record_data = sanitize_record(record_data)

    upload_filename = "data.zip"

    with UnitOfWork(db.session) as uow:

        # Create draft
        draft = current_rdm_records_service.create(
            system_identity,
            record_data,
            uow=uow
        )

        files_service = current_rdm_records_service.draft_files

        # Initialize file
        files_service.init_files(
            system_identity,
            draft.id,
            data=[{"key": Path(upload_filename).name}],
            uow=uow
        )

        # Upload file
        with open(upload_filename, "rb") as f:
            files_service.set_file_content(
                system_identity,
                draft.id,
                Path(upload_filename).name,
                f,
                uow=uow
            )

        # Commit file
        files_service.commit_file(
            system_identity,
            draft.id,
            Path(upload_filename).name,
            uow=uow
        )

        # Publish record
        record = current_rdm_records_service.publish(
            system_identity,
            draft.id,
            uow=uow
        )

        uow.commit()

    return record


# Usage
record = create_record_from_file()