from tap_contentful.streams.abstracts import ChildBaseStream

class Tasks(ChildBaseStream):
    tap_stream_id = "tasks"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments/{environment_id}/tasks?filter=myPendingTasks"
    parent = "environments"
    bookmark_value = None

