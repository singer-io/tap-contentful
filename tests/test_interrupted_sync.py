
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
            "currently_syncing": "environments",
            "bookmarks": {
                "environments": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "organizations": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "security_contacts": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "content_types": { "updatedAt" : "2020-01-01T00:00:00Z"},
                # "environment_templates": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "entries": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "assets": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "locales": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "taxonomy_concepts": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "tags": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "tasks": { "updatedAt" : "2020-01-01T00:00:00Z"},
        }
    }
