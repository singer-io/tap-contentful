from base import contentfulBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class contentfulBookMarkTest(BookmarkTest, contentfulBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    initial_bookmarks = {
        "bookmarks": {
            "content_types": { "updatedAt" : "2024-10-10T00:00:00Z"},
            "entries": { "updatedAt" : "2024-01-01T00:00:00Z"},
            "assets": { "updatedAt" : "2024-10-10T00:00:00Z"},
            "taxonomy_concepts": { "updatedAt" : "2024-10-10T00:00:00Z"},
            "tags": { "updatedAt" : "2025-01-01T00:00:00Z"},
        }
    }
    @staticmethod
    def name():
        return "tap_tester_contentful_bookmark_test"

    def streams_to_test(self):
        streams_to_exclude = {
            # Less data available for streams
            'security_contacts',
            'tasks',
            'locales',
            # Unsupported Full-Table Streams
            'environments',
            'organizations',
            # Not have permission
            'environment_templates'
        }
        return self.expected_stream_names().difference(streams_to_exclude)

    def calculate_new_bookmarks(self):
        """Calculates new bookmarks by looking through sync 1 data to determine
        a bookmark that will sync 2 records in sync 2 (plus any necessary look
        back data)"""
        new_bookmarks = {
            "content_types": { "updatedAt" : "2025-10-12T00:00:00Z"},
            "entries": { "updatedAt" : "2025-11-09T00:00:00Z"},
            "assets": { "updatedAt" : "2025-10-12T00:00:00Z"},
            "taxonomy_concepts": { "updatedAt" : "2025-10-12T00:00:00Z"},
            "tags": { "updatedAt" : "2025-10-07T06:33:00.00Z"},

        }

        return new_bookmarks