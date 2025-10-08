from base import contentfulBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class contentfulBookMarkTest(BookmarkTest, contentfulBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    initial_bookmarks = {
        "bookmarks": {
            "environments": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "organizations": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "security_contacts": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "content_types": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "environment_templates": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "entries": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "assets": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "locales": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "taxonomy_concepts": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "tags": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
            "tasks": { "sys.updatedAt" : "2020-01-01T00:00:00Z"},
        }
    }
    @staticmethod
    def name():
        return "tap_tester_contentful_bookmark_test"

    def streams_to_test(self):
        streams_to_exclude = {}
        return self.expected_stream_names().difference(streams_to_exclude)

