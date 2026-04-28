import json
import sys
from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork


def get_draft_info(record_id):
    """Get information about a draft record."""
    try:
        draft = current_rdm_records_service.read_draft(system_identity, record_id)
        return draft
    except Exception as e:
        print(f"✗ Error reading draft: {e}")
        return None


def publish_record(record_id):
    """Publish a draft record."""
    
    print(f"=== PUBLISHING RECORD {record_id} ===")
    
    # Get draft info first
    draft = get_draft_info(record_id)
    if not draft:
        return False
    
    print(f"Title: {draft.data['metadata'].get('title', 'No title')}")
    print(f"Status: {draft.data.get('status', 'unknown')}")
    
    try:
        with UnitOfWork(db.session) as uow:
            print("Publishing record...")
            
            # Publish the draft
            published_record = current_rdm_records_service.publish(
                system_identity, record_id, uow=uow
            )
            
            uow.commit()
            
            print(f"✓ Successfully published record!")
            print(f"Published record ID: {published_record.id}")
            print(f"Title: {published_record.data['metadata'].get('title', 'No title')}")
            
            return published_record
            
    except Exception as e:
        print(f"✗ Error publishing record: {e}")
        print(f"Details: {str(e)}")
        return False


def main():
    """Interactive record publisher."""
    
    print("=== INVENIO RECORD PUBLISHER ===\n")
    
    # Hard-coded record ID
    record_id = "zxh03-edp73"
    print(f"Publishing record: {record_id}")
    
    # Get current draft info
    draft = get_draft_info(record_id)
    if not draft:
        return
    
    title = draft.data['metadata'].get('title', 'No title')
    print(f"Draft title: {title}")
    
    # Confirm publishing
    print(f"\nReady to publish:")
    print(f"Record ID: {record_id}")
    print(f"Title: {title}")
    
    confirm = input("Publish this draft? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Publish the record
    result = publish_record(record_id)
    
    if result:
        print(f"\n✓ Record published successfully!")
        print(f"You can now view it in the web interface.")
    else:
        print(f"\n✗ Failed to publish record.")


if __name__ == "__main__":
    main()