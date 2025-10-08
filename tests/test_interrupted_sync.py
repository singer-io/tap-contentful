
from base import contentfulBaseTest
from tap_tester.base_suite_tests.interrupted_sync_test import InterruptedSyncTest


class contentfulInterruptedSyncTest(InterruptedSyncTest, contentfulBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""

    @staticmethod
    def name():
        return "tap_tester_contentful_interrupted_sync_test"

    def streams_to_test(self):
        return self.expected_stream_names()


    def manipulate_state(self):
        return {
            "currently_syncing": "prospects",
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

