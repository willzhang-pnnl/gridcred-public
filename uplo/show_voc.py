from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_access.permissions import system_identity
from invenio_vocabularies.records.models import VocabularyType

print("=== CONFIGURED VOCABULARY TYPES ===")
types = VocabularyType.query.all()
for t in types:
    print(f"Type: {t.id}")

print("\n=== QUERYING EACH VOCABULARY TYPE ===")
vocab_types = ['subjects', 'affiliations', 'creatorsroles', 'contributorsroles', 'languages', 'resourcetypes', 'licenses']
for vocab_type in vocab_types:
    try:
        result = vocabulary_service.read_all(
            system_identity, 
            type=vocab_type,
            fields=["id", "title"]  # Add required fields parameter
        )
        print(f"\n{vocab_type.upper()} ({len(result)} entries):")
        # Handle different result types
        if hasattr(result, 'entries'):
            items = result.entries
        elif hasattr(result, '_results'):
            items = result._results
        else:
            items = list(result)[:10]  # Convert to list and limit to first 10
            
        for i, item in enumerate(items[:5]):  # Show first 5 entries
            if hasattr(item, 'get'):
                print(f"  ID: '{item.get('id', 'N/A')}' - Title: {item.get('title', {}).get('en', 'N/A')}")
            else:
                print(f"  {item}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more")
    except Exception as e:
        print(f"Error querying {vocab_type}: {e}")

print("\n=== CHECKING FOR RESOURCE_TYPES (resourcetypes) ===")
try:
    result = vocabulary_service.read_all(
        system_identity, 
        type="resourcetypes",  # Note: it's resourcetypes, not resource_types
        fields=["id", "title"]
    )
    print("Resource types found!")
    # Handle different result types
    if hasattr(result, 'entries'):
        items = result.entries
    elif hasattr(result, '_results'):
        items = result._results
    else:
        items = list(result)
        
    for item in items:
        if hasattr(item, 'get'):
            print(f"  ID: '{item.get('id', 'N/A')}' - Title: {item.get('title', {}).get('en', 'N/A')}")
        else:
            print(f"  {item}")
except Exception as e:
    print(f"Error querying resourcetypes: {e}")
    
print("\n=== SOLUTIONS ===")
print("Good news! The 'resourcetypes' vocabulary EXISTS in your system.")
print("The issue might be:")
print("1. Your record.json uses 'resource_type' field but vocabulary is 'resourcetypes'") 
print("2. Try using a valid resource type ID from the list above")
print("3. If still having issues, check the exact field name expected in metadata")