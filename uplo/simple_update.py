from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork
from datetime import date

# Hard-coded values
RECORD_ID = "qcdqh-7gc67"
NEW_TITLE = "Updated Brackish Groundwater Dataset"

print(f"Updating title for record: {RECORD_ID}")
print(f"New title: {NEW_TITLE}")

with UnitOfWork(db.session) as uow:
    # Create new version
    new_version = current_rdm_records_service.new_version(
        system_identity, RECORD_ID, uow=uow
    )
    
    new_record_id = new_version.id
    print(f"Created new version: {new_record_id}")
    
    # Get the draft
    draft = current_rdm_records_service.read_draft(system_identity, new_record_id)
    
    # Update title and ensure required fields are set
    updated_data = draft.data.copy()
    updated_data['metadata']['title'] = NEW_TITLE
    
    # Ensure publication_date is set (use today's date if missing)
    if 'publication_date' not in updated_data['metadata']:
        updated_data['metadata']['publication_date'] = str(date.today())
        print(f"Added publication_date: {updated_data['metadata']['publication_date']}")
    
    # Save updated draft
    current_rdm_records_service.update_draft(
        system_identity, new_record_id, updated_data, uow=uow
    )
    
    # Publish it
    published_record = current_rdm_records_service.publish(
        system_identity, new_record_id, uow=uow
    )
    
    uow.commit()
    
    print(f"✓ Published new version: {published_record.id}")
    print(f"✓ Title updated to: {NEW_TITLE}")