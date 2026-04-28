from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def update_existing_file(record_id, file_path="data.zip"):
    file_path = Path(file_path)
    filename = file_path.name

    files_service = current_rdm_records_service.draft_files

    with UnitOfWork(db.session) as uow:
        # create new version draft
        draft = current_rdm_records_service.edit(
            system_identity,
            record_id,
            uow=uow,
        )

        # DO NOT init_files again (already exists)

        # overwrite file content only
        with open(file_path, "rb") as fp:
            files_service.set_file_content(
                system_identity,
                draft.id,
                filename,
                fp,
                uow=uow,
            )

        files_service.commit_file(
            system_identity,
            draft.id,
            filename,
            uow=uow,
        )

        record = current_rdm_records_service.publish(
            system_identity,
            draft.id,
            uow=uow,
        )

        uow.commit()

    print(f"✅ Updated file for record {record_id}")


# RUN
if __name__ == "__main__":
    update_existing_file("d1arf-v1m22", "data.zip")