import json
from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def reupload_file_to_record(record_id, file_path="data.zip"):
    """Reupload a file to an existing record."""

    file_path = Path(file_path)
    filename = file_path.name

    files_service = current_rdm_records_service.files

    with UnitOfWork(db.session) as uow:
        # Step 1: Initialize file entry (creates or overwrites metadata)
        files_service.init_files(
            system_identity,
            record_id,
            data=[{"key": filename}],
            uow=uow,
        )

        # Step 2: Upload file content
        with open(file_path, "rb") as f:
            files_service.set_file_content(
                system_identity,
                record_id,
                filename,
                f,
                uow=uow,
            )

        # Step 3: Commit file (VERY IMPORTANT — missing this causes NoSuchKey)
        files_service.commit_file(
            system_identity,
            record_id,
            filename,
            uow=uow,
        )

        uow.commit()

    print(f"✅ Reuploaded file '{filename}' to record {record_id}")


# Usage
reupload_file_to_record("YOUR_RECORD_ID_HERE", "data.zip")