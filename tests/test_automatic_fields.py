"""Test that with no fields selected for a stream automatic fields are still
replicated."""
from base import contentfulBaseTest
from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest


class contentfulAutomaticFields(MinimumSelectionTest, contentfulBaseTest):
    """Test that with no fields selected for a stream automatic fields are
    still replicated."""

    @staticmethod
    def name():
        return "tap_tester_contentful_automatic_fields_test"

    def streams_to_test(self):
        streams_to_exclude = {'tasks', 'security_contacts', 'environment_templates',
                              'locales', 'tags'}
        # return self.expected_stream_names().difference(streams_to_exclude)
        return {'environments', 'organizations'}
