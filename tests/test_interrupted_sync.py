
from base import contentfulBaseTest
from tap_tester.base_suite_tests.interrupted_sync_test import InterruptedSyncTest


class contentfulInterruptedSyncTest(InterruptedSyncTest, contentfulBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""

    @staticmethod
    def name():
        return "tap_tester_contentful_interrupted_sync_test"

    def streams_to_test(self):
        streams_to_exclude = {'security_contacts', 'tasks', 'environment_templates', 'environments', 'organizations', 'content_types'}
        return self.expected_stream_names().difference(streams_to_exclude)


    def manipulate_state(self):
        return {
            "currently_syncing": "entries",
            "bookmarks": {
                "entries": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "assets": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "locales": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "taxonomy_concepts": { "updatedAt" : "2020-01-01T00:00:00Z"},
                "tags": { "updatedAt" : "2020-01-01T00:00:00Z"},
        }
    }
