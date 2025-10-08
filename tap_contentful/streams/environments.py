from tap_contentful.streams.abstracts import ChildBaseStream

class Environments(ChildBaseStream):
    tap_stream_id = "environments"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments"
    parent = "spaces"
    bookmark_value = None
    children = ["content_types", "entries", "assets", "locales", "tags", "tasks"]

