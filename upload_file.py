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
        # 1. Create draft
        draft = current_rdm_records_service.edit(
            system_identity,
            record_id,
            uow=uow,
        )

        # 2. Delete ALL existing files (important for locked bucket)
        existing_files = files_service.list_files(
            system_identity,
            draft.id,
        )

        for f in existing_files.entries:
            files_service.delete_file(
                system_identity,
                draft.id,
                f.key,
                uow=uow,
            )

        # 3. Initialize new file
        files_service.init_files(
            system_identity,
            draft.id,
            data=[{"key": filename}],
            uow=uow,
        )

        # 4. Upload new content
        with open(file_path, "rb") as fp:
            files_service.set_file_content(
                system_identity,
                draft.id,
                filename,
                fp,
                uow=uow,
            )

        # 5. Commit
        files_service.commit_file(
            system_identity,
            draft.id,
            filename,
            uow=uow,
        )

        # 6. Publish (creates NEW version + new bucket linkage)
        record = current_rdm_records_service.publish(
            system_identity,
            draft.id,
            uow=uow,
        )

        uow.commit()

    print(f"✅ File replaced for record {record_id}")