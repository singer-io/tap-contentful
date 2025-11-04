from base import contentfulBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class contentfulBookMarkTest(BookmarkTest, contentfulBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    initial_bookmarks = {
        "bookmarks": {
            "environments": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "organizations": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "security_contacts": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "content_types": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "environment_templates": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "entries": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "assets": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "locales": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "taxonomy_concepts": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "tags": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "tasks": { "updatedAt" : "2020-01-01T00:00:00Z"},
        }
    }
    @staticmethod
    def name():
        return "tap_tester_contentful_bookmark_test"

    def streams_to_test(self):
        streams_to_exclude = {'expected_stream_names', 'security_contacts', 'tasks'}
        return self.expected_stream_names().difference(streams_to_exclude)
