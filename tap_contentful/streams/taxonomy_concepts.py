from tap_contentful.streams.abstracts import ChildBaseStream

class TaxonomyConcepts(ChildBaseStream):
    tap_stream_id = "taxonomy_concepts"
    key_properties = "id"
    replication_method = "INCREMENTAL"
    replication_keys = ["updatedAt"]
    data_key = "items"
    path = "/organizations/{organizationId}/taxonomy/concepts"
    parent = "organizations"
    bookmark_value = None

    def get_url_endpoint(self, parent_obj=None):
        """Prepare URL endpoint for child streams."""
        env_id = self.get_nested_value(parent_obj, 'sys.id')
        return f"{self.client.base_url}{self.path.format(organizationId=env_id)}"
