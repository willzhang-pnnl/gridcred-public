from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def reupload_file_via_draft(record_id, file_path="data.zip"):
    file_path = Path(file_path)
    filename = file_path.name

    files_service = current_rdm_records_service.draft_files

    with UnitOfWork(db.session) as uow:
        # Step 1: Create draft from existing record
        draft = current_rdm_records_service.edit(
            system_identity,
            record_id,
            uow=uow,
        )

        # Step 2: (optional) delete existing file if present
        try:
            files_service.delete_file(
                system_identity,
                draft.id,
                filename,
                uow=uow,
            )
        except Exception:
            pass  # file may not exist, ignore

        # Step 3: Initialize file
        files_service.init_files(
            system_identity,
            draft.id,
            data=[{"key": filename}],
            uow=uow,
        )

        # Step 4: Upload content
        with open(file_path, "rb") as f:
            files_service.set_file_content(
                system_identity,
                draft.id,
                filename,
                f,
                uow=uow,
            )

        # Step 5: Commit file (critical)
        files_service.commit_file(
            system_identity,
            draft.id,
            filename,
            uow=uow,
        )

        # Step 6: Publish new version
        record = current_rdm_records_service.publish(
            system_identity,
            draft.id,
            uow=uow,
        )

        uow.commit()

    print(f"✅ File reuploaded and record {record_id} updated")


# Usage
reupload_file_via_draft("d1arf-v1m22", "data.zip")