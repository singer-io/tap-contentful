from tap_contentful.streams.abstracts import ChildBaseStream

class Entries(ChildBaseStream):
    tap_stream_id = "entries"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments/{environment_id}/entries"
    parent = "environments"
    bookmark_value = None

