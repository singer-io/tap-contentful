from tap_contentful.streams.abstracts import ChildBaseStream

class EnvironmentTemplates(ChildBaseStream):
    tap_stream_id = "environment_templates"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/organizations/{organization_id}/environment_templates"
    parent = "organizations"
    bookmark_value = None

