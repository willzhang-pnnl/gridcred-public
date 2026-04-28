from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork

# Hard-coded record ID to delete
RECORD_ID = "qcdqh-7gc67"  # Change this to the record you want to delete

print(f"Deleting record: {RECORD_ID}")

try:
    # First, check if the record exists
    try:
        record = current_rdm_records_service.read(system_identity, RECORD_ID)
        title = record.data['metadata'].get('title', 'No title')
        print(f"Found record: {title}")
    except Exception as e:
        print(f"✗ Error reading record: {e}")
        print("Record may not exist or may be a draft.")
        exit(1)

    # Confirm deletion
    print(f"\n⚠️  WARNING: This will permanently delete the record!")
    print(f"Record ID: {RECORD_ID}")
    print(f"Title: {title}")
    confirm = input("Type 'DELETE' to confirm deletion: ").strip()
    
    if confirm != "DELETE":
        print("Deletion cancelled.")
        exit(0)

    # Delete the record
    with UnitOfWork(db.session) as uow:
        print("Deleting record...")
        current_rdm_records_service.delete_record(
            system_identity, RECORD_ID, uow=uow
        )
        uow.commit()
        print(f"✓ Record {RECORD_ID} has been deleted successfully!")

except Exception as e:
    print(f"✗ Error deleting record: {e}")
    print(f"Details: {str(e)}")