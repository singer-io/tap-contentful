from tap_contentful.streams.abstracts import FullTableStream

class Organizations(FullTableStream):
    tap_stream_id = "organizations"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    data_key = "items"
    path = "/organizations"
    children = ["security_contacts", "environment_templates", "taxonomy_concepts"]

    def modify_object(self, record, parent_record=None):
            """
            Modify the record before writing to the stream.
            Move sys.id -> id and sys.updatedAt -> updatedAt
            """
            sys_data = record.get("sys", {})

            record["id"] = sys_data.get("id")

            return record
