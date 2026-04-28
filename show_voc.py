from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_access.permissions import system_identity
from invenio_vocabularies.records.models import VocabularyType

print("=== CONFIGURED VOCABULARY TYPES ===")
types = VocabularyType.query.all()
for t in types:
    print(f"Type: {t.id}")

print("\n=== QUERYING EACH VOCABULARY TYPE ===")
for vocab_type in ['subjects', 'affiliations', 'creatorsroles', 'contributorsroles', 'languages']:
    try:
        result = vocabulary_service.read_all(
            system_identity, 
            type=vocab_type,
            fields=["id", "title"]  # Add required fields parameter
        )
        print(f"\n{vocab_type.upper()} ({len(result.entries)} entries):")
        for item in result.entries[:5]:  # Show first 5 entries
            print(f"  ID: '{item['id']}' - Title: {item.get('title', {}).get('en', 'N/A')}")
        if len(result.entries) > 5:
            print(f"  ... and {len(result.entries) - 5} more")
    except Exception as e:
        print(f"Error querying {vocab_type}: {e}")

print("\n=== CHECKING FOR RESOURCE_TYPES ===")
try:
    result = vocabulary_service.read_all(
        system_identity, 
        type="resource_types",
        fields=["id", "title"]
    )
    print("Resource types found!")
    for item in result.entries:
        print(f"  ID: '{item['id']}' - Title: {item.get('title', {}).get('en', 'N/A')}")
except Exception as e:
    print(f"resource_types vocabulary does not exist: {e}")
    
print("\n=== SOLUTIONS ===")
print("Since resource_types vocabulary is missing, you have 3 options:")
print("1. Remove the resource_type field from your record.json")
print("2. Import/configure the resource_types vocabulary")  
print("3. Use a different field structure that doesn't require resource_type")