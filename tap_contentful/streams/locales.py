from tap_contentful.streams.abstracts import ChildBaseStream

class Locales(ChildBaseStream):
    tap_stream_id = "locales"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments/{environment_id}/locales"
    parent = "environments"
    bookmark_value = None

