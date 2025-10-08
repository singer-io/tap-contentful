from tap_contentful.streams.abstracts import ChildBaseStream

class TaxonomyConcepts(ChildBaseStream):
    tap_stream_id = "taxonomy_concepts"
    key_properties = "sys.id"
    replication_method = "INCREMENTAL"
    replication_keys = ["sys.updatedAt"]
    data_key = "items"
    path = "/organizations/{organizationId}/taxonomy/concepts"
    parent = "organizations"
    bookmark_value = None

