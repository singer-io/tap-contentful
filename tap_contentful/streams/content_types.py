from tap_contentful.streams.abstracts import ChildBaseStream

class ContentTypes(ChildBaseStream):
    tap_stream_id = "content_types"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments/{environment_id}/content_types"
    parent = "environments"
    bookmark_value = None

