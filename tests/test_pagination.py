from tap_tester.base_suite_tests.pagination_test import PaginationTest
from base import contentfulBaseTest

class contentfulPaginationTest(PaginationTest, contentfulBaseTest):
    """
    Ensure tap can replicate multiple pages of data for streams that use pagination.
    """

    @staticmethod
    def name():
        return "tap_tester_contentful_pagination_test"

    def streams_to_test(self):
        streams_to_exclude = {'expected_stream_names', 'tasks', 'security_contacts'}
        return self.expected_stream_names().difference(streams_to_exclude)
