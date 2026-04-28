from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_access.permissions import system_identity

# List available resource types
try:
    result = vocabulary_service.read_all(system_identity, type="resource_types")
    print("Available resource types:")
    for item in result.entries:
        print(f"ID: '{item['id']}' - Title: {item.get('title', {}).get('en', 'N/A')}")
except Exception as e:
    print(f"Error querying resource_types: {e}")

# Also check what vocabulary types are configured
try:
    from invenio_vocabularies.records.models import VocabularyType
    types = VocabularyType.query.all()
    print(f"\nConfigured vocabulary types: {[t.id for t in types]}")
except Exception as e:
    print(f"Error getting vocabulary types: {e}")