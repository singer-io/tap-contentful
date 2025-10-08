from tap_contentful.streams.abstracts import ChildBaseStream

class Tags(ChildBaseStream):
    tap_stream_id = "tags"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments/{environment_id}/tags"
    parent = "environments"
    bookmark_value = None

