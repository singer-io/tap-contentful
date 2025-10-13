from tap_contentful.streams.abstracts import ChildBaseStream

class Assets(ChildBaseStream):
    tap_stream_id = "assets"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments/{environment_id}/assets"
    parent = "environments"
    bookmark_value = None

    def get_url_endpoint(self, parent_obj=None):
        """Prepare URL endpoint for child streams."""
        env_id = self.get_nested_value(parent_obj, 'sys.id')
        return f"{self.client.base_url}{self.path.format(space_id=self.client.config['space_id'], environment_id=env_id)}"
    
    def update_params(self, date = None, **kwargs) -> None:
        """
        Update params for the stream
        """
        self.params.update({'sys.updatedAt[gte]': date})
