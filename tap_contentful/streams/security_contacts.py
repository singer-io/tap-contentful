from tap_contentful.streams.abstracts import ChildBaseStream

class SecurityContacts(ChildBaseStream):
    tap_stream_id = "security_contacts"
    key_properties = ["sys.id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/organizations/{organization_id}/security_contacts"
    parent = "organizations"
    bookmark_value = None

    def get_url_endpoint(self, parent_obj=None):
        """Prepare URL endpoint for child streams."""
        env_id = self.get_nested_value(parent_obj, 'sys.id')
        return f"{self.client.base_url}{self.path.format(organization_id=env_id)}"

