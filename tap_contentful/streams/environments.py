from tap_contentful.streams.abstracts import ParentBaseStream
from typing import Dict

class Environments(ParentBaseStream):
    tap_stream_id = "environments"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/spaces/{space_id}/environments"
    children = ["content_types", "entries", "assets", "locales", "tags", "tasks"]

    def get_url_endpoint(self, parent_obj: Dict = None) -> str:
        """
        Get the URL endpoint for the stream
        """
        space_id = self.client.config.get("space_id")
        formatted_path = self.path.format(space_id=space_id)
        return self.url_endpoint or f"{self.client.base_url}{formatted_path}"
