from tap_contentful.streams.abstracts import ChildBaseStream

class Assets(ChildBaseStream):
    tap_stream_id = "assets"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments/{environment_id}/assets"
    parent = "environments"
    bookmark_value = None

    def get_url_endpoint(self, parent_obj=None):
        """Prepare URL endpoint for child streams."""
        env_id = self.get_nested_value(parent_obj, 'id')
        return f"{self.client.base_url}{self.path.format(space_id=self.client.config['space_id'], environment_id=env_id)}"

    def modify_object(self, record, parent_record=None):
            """
            Modify the record before writing to the stream.
            Move sys.id -> id and sys.updatedAt -> updatedAt
            """
            sys_data = record.get("sys", {})

            record["id"] = sys_data.get("id")
            record["updatedAt"] = sys_data.get("updatedAt")

            return record
