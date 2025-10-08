from tap_contentful.streams.abstracts import ChildBaseStream

class SecurityContacts(ChildBaseStream):
    tap_stream_id = "security_contacts"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/organizations/{organization_id}/security_contacts"
    parent = "organizations"
    bookmark_value = None

