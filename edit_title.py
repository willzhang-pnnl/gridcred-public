import json
import sys
from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def get_record_info(record_id):
    """Get information about a record."""
    try:
        # Try to read as draft first
        try:
            record = current_rdm_records_service.read_draft(system_identity, record_id)
            print(f"✓ Found DRAFT record")
            return record, "draft"
        except:
            # Try to read as published record
            record = current_rdm_records_service.read(system_identity, record_id)
            print(f"✓ Found PUBLISHED record")
            return record, "published"
    except Exception as e:
        print(f"✗ Error finding record: {e}")
        return None, None


def update_record_title(record_id, new_title):
    """Update record title with appropriate method."""
    
    print(f"\n=== UPDATING RECORD {record_id} ===")
    
    # Get record info first
    record, record_type = get_record_info(record_id)
    if not record:
        return False
    
    current_title = record.data['metadata'].get('title', 'No title')
    print(f"Current title: {current_title}")
    print(f"New title: {new_title}")
    print(f"Record type: {record_type}")
    
    try:
        with UnitOfWork(db.session) as uow:
            if record_type == "draft":
                # Update draft directly
                print("Updating draft...")
                updated_data = record.data.copy()
                updated_data['metadata']['title'] = new_title
                
                updated_record = current_rdm_records_service.update_draft(
                    system_identity, record_id, updated_data, uow=uow
                )
                
            elif record_type == "published":
                # Create new version for published records
                print("Creating new version of published record...")
                new_version = current_rdm_records_service.new_version(
                    system_identity, record_id, uow=uow
                )
                
                new_record_id = new_version.id
                print(f"New version created: {new_record_id}")
                
                # Update the new version's title
                draft = current_rdm_records_service.read_draft(system_identity, new_record_id)
                updated_data = draft.data.copy()
                updated_data['metadata']['title'] = new_title
                
                updated_record = current_rdm_records_service.update_draft(
                    system_identity, new_record_id, updated_data, uow=uow
                )
                
                print(f"Updated new version {new_record_id} with new title")
            
            uow.commit()
            print(f"✓ Successfully updated title!")
            return True
            
    except Exception as e:
        print(f"✗ Error updating record: {e}")
        return False


def main():
    """Interactive record editor."""
    
    print("=== INVENIO RECORD TITLE EDITOR ===\n")
    
    # Get record ID
    if len(sys.argv) > 1:
        record_id = sys.argv[1]
    else:
        record_id = input("Enter record ID (e.g., qcdqh-7gc67): ").strip()
    
    if not record_id:
        print("No record ID provided!")
        return
    
    # Get current record info
    record, record_type = get_record_info(record_id)
    if not record:
        return
    
    current_title = record.data['metadata'].get('title', 'No title')
    print(f"\nCurrent title: {current_title}")
    
    # Get new title
    if len(sys.argv) > 2:
        new_title = " ".join(sys.argv[2:])
    else:
        new_title = input("Enter new title: ").strip()
    
    if not new_title:
        print("No new title provided!")
        return
    
    # Confirm the change
    print(f"\nReady to update:")
    print(f"Record ID: {record_id}")
    print(f"From: {current_title}")
    print(f"To: {new_title}")
    
    if len(sys.argv) <= 2:  # Only ask for confirmation in interactive mode
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
    
    # Make the update
    success = update_record_title(record_id, new_title)
    
    if success:
        print(f"\n✓ Record updated successfully!")
    else:
        print(f"\n✗ Failed to update record.")


if __name__ == "__main__":
    main()