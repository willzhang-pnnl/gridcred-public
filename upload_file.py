from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def replace_file(record_id, file_path="data.zip"):
    file_path = Path(file_path)
    filename = file_path.name

    files_service = current_rdm_records_service.draft_files

    with UnitOfWork(db.session) as uow:
        # Create draft from record
        draft = current_rdm_records_service.edit(
            system_identity,
            record_id,
            uow=uow,
        )

        # List existing files
        existing_files = files_service.list_files(
            system_identity,
            draft.id,
        )

        # FIX: dict access instead of attribute access
        for f in existing_files.entries:
            files_service.delete_file(
                system_identity,
                draft.id,
                f["key"],   # <-- FIXED HERE
                uow=uow,
            )

        # Init new file
        files_service.init_files(
            system_identity,
            draft.id,
            data=[{"key": filename}],
            uow=uow,
        )

        # Upload content
        with open(file_path, "rb") as fp:
            files_service.set_file_content(
                system_identity,
                draft.id,
                filename,
                fp,
                uow=uow,
            )

        # Commit
        files_service.commit_file(
            system_identity,
            draft.id,
            filename,
            uow=uow,
        )

        # Publish new version
        record = current_rdm_records_service.publish(
            system_identity,
            draft.id,
            uow=uow,
        )

        uow.commit()

    print(f"✅ Replaced file for record {record_id}")


# RUN
if __name__ == "__main__":
    replace_file("d1arf-v1m22", "data.zip")