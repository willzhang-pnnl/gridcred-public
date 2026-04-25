import json
from pathlib import Path
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_access.permissions import system_identity
from invenio_db import db
from invenio_records_resources.services.uow import UnitOfWork
from io import BytesIO


def create_record_from_file(filename="record-zen.json"):
    """Create and publish a record by reading JSON from a file."""

    # Read record data from file in same directory
    script_dir = Path(__file__).parent
    record_file = script_dir / filename

    with open(record_file, 'r') as f:
        record_data = json.load(f)

    with UnitOfWork(db.session) as uow:
        # Create draft with data from file
        draft = current_rdm_records_service.create(
            system_identity, record_data, uow=uow
        )

        files_service = current_rdm_records_service.draft_files  
              
        # Use the provided file or default to data.zip  
        upload_filename = "data.zip"  
          
        files_service.init_files(  
            system_identity, draft.id, data=[{"key": Path(upload_filename).name}], uow=uow  
        )  
          
        # Open and upload the existing file  
        with open(upload_filename, 'rb') as f:  
            files_service.set_file_content(  
                system_identity, draft.id, Path(upload_filename).name,   
                f, uow=uow  
            )  
          
        files_service.commit_file(  
            system_identity, draft.id, Path(upload_filename).name, uow=uow  
        )  
        

        # Publish the record  
        
        record = current_rdm_records_service.publish(  
            system_identity, draft.id, uow=uow  
        )  
        

        uow.commit()  
          
    return record  
  
# Usage  
record = create_record_from_file()  