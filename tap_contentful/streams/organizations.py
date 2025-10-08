from tap_contentful.streams.abstracts import ParentBaseStream

class Organizations(ParentBaseStream):
    tap_stream_id = "organizations"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/organizations"
    children = ["security_contacts", "environment_templates", "taxonomy_concepts"]

