import json
from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def edit_record_title(record_id, new_title):
    """Edit the title of an existing record."""
    
    print(f"Editing record: {record_id}")
    print(f"New title: {new_title}")
    
    try:
        with UnitOfWork(db.session) as uow:
            # Get the existing record
            print("Retrieving existing record...")
            record = current_rdm_records_service.read_draft(
                system_identity, record_id
            )
            
            print(f"Current title: {record.data['metadata'].get('title', 'No title')}")
            
            # Update the title in the metadata
            updated_data = record.data.copy()
            updated_data['metadata']['title'] = new_title
            
            # Update the record
            print("Updating record...")
            updated_record = current_rdm_records_service.update_draft(
                system_identity, record_id, updated_data, uow=uow
            )
            
            # Commit the changes
            uow.commit()
            
            print(f"✓ Successfully updated title to: {new_title}")
            print(f"Record ID: {record_id}")
            
            return updated_record
            
    except Exception as e:
        print(f"✗ Error updating record: {e}")
        
        # Try to read as published record if draft doesn't exist
        try:
            print("Trying to read as published record...")
            record = current_rdm_records_service.read(
                system_identity, record_id
            )
            print(f"Found published record with title: {record.data['metadata'].get('title', 'No title')}")
            print("Note: Cannot directly edit published records. You may need to create a new version or edit draft.")
            return None
        except Exception as e2:
            print(f"✗ Error reading published record: {e2}")
            return None


def create_new_version_and_edit(record_id, new_title):
    """Create a new version of a published record and edit its title."""
    
    print(f"Creating new version of record: {record_id}")
    
    try:
        with UnitOfWork(db.session) as uow:
            # Create new version
            print("Creating new version...")
            new_version = current_rdm_records_service.new_version(
                system_identity, record_id, uow=uow
            )
            
            new_record_id = new_version.id
            print(f"New version created with ID: {new_record_id}")
            
            # Get the draft of the new version
            draft = current_rdm_records_service.read_draft(
                system_identity, new_record_id
            )
            
            # Update the title
            updated_data = draft.data.copy()
            updated_data['metadata']['title'] = new_title
            
            # Update the draft
            updated_record = current_rdm_records_service.update_draft(
                system_identity, new_record_id, updated_data, uow=uow
            )
            
            uow.commit()
            
            print(f"✓ Successfully created new version and updated title to: {new_title}")
            print(f"New record ID: {new_record_id}")
            print("Note: This is a draft. Use publish_record.py to publish it.")
            
            return updated_record
            
    except Exception as e:
        print(f"✗ Error creating new version: {e}")
        return None


if __name__ == "__main__":
    # Configuration
    RECORD_ID = "qcdqh-7gc67"
    NEW_TITLE = "Updated Brackish Groundwater"
    
    print("=== RECORD TITLE EDITOR ===")
    print(f"Target record: {RECORD_ID}")
    print(f"New title: {NEW_TITLE}")
    print()
    
    # Try to edit the record directly (works if it's a draft)
    result = edit_record_title(RECORD_ID, NEW_TITLE)
    
    # If that failed, try creating a new version (for published records)
    if result is None:
        print("\n=== TRYING NEW VERSION APPROACH ===")
        result = create_new_version_and_edit(RECORD_ID, NEW_TITLE)
    
    if result:
        print(f"\n✓ Operation completed successfully!")
    else:
        print(f"\n✗ Failed to update record. Check the record ID and permissions.")