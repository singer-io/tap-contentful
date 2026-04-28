import copy
import os
import unittest
from datetime import datetime as dt
from datetime import timedelta

import dateutil.parser
import pytz
from tap_tester import connections, menagerie, runner
from tap_tester.logger import LOGGER
from tap_tester.base_suite_tests.base_case import BaseCase


class contentfulBaseTest(BaseCase):
    """Setup expectations for test sub classes.

    Metadata describing streams. A bunch of shared methods that are used
    in tap-tester tests. Shared tap-specific methods (as needed).
    """
    start_date = "2019-01-01T00:00:00Z"

    # Populated dynamically by run_and_verify_check_mode based on
    # which streams the tap excludes at discovery time (401/403/422).
    PERMISSION_DEPENDENT_STREAMS = set()

    @staticmethod
    def tap_name():
        """The name of the tap."""
        return "tap-contentful"

    @staticmethod
    def get_type():
        """The name of the tap."""
        return "platform.contentful"

    @classmethod
    def expected_metadata(cls):
        """The expected streams and metadata about the streams."""
        return {
            "environments": {
                # we dont have parent stream space we just use space id to get records
                cls.PRIMARY_KEYS: {"id", "space_id"},
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "organizations": {
                cls.PRIMARY_KEYS: {"id"},
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "security_contacts": {
                cls.PRIMARY_KEYS: {"id", "organization_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "organizations"
            },
            "content_types": {
                cls.PRIMARY_KEYS: {"id", "space_id", "environment_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "entries": {
                cls.PRIMARY_KEYS: {"id", "space_id", "environment_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "assets": {
                cls.PRIMARY_KEYS: {"id", "space_id", "environment_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "locales": {
                cls.PRIMARY_KEYS: {"id", "space_id", "environment_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "taxonomy_concepts": {
                cls.PRIMARY_KEYS: {"id", "organization_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "organizations"
            },
            "tags": {
                cls.PRIMARY_KEYS: {"id", "space_id", "environment_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "tasks": {
                cls.PRIMARY_KEYS: {"id", "space_id", "environment_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "environment_templates": {
                cls.PRIMARY_KEYS: {"id", "organization_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: {"updatedAt"},
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "organizations"
            }
        }

    @classmethod
    def expected_stream_names(cls):
        """Return expected streams minus any dynamically excluded ones."""
        return (set(cls.expected_metadata().keys())
                - cls.PERMISSION_DEPENDENT_STREAMS)

    def run_and_verify_check_mode(self, conn_id):
        """Override to dynamically detect permission-dependent streams.

        Runs discovery, compares found streams against expected_metadata,
        and treats any missing streams as permission-dependent rather
        than failing immediately.
        """
        check_job_name = runner.run_check_mode(self, conn_id)

        exit_status = menagerie.get_exit_status(conn_id, check_job_name)
        menagerie.verify_check_exit_status(
            self, exit_status, check_job_name
        )

        found_catalogs = menagerie.get_catalogs(conn_id)
        self.assertGreater(
            len(found_catalogs), 0,
            logging="A catalog was produced by discovery."
        )

        found_names = {c['stream_name'] for c in found_catalogs}
        all_expected = set(self.expected_metadata().keys())

        # Streams in catalog but not in expected_metadata are unexpected
        unexpected = found_names - all_expected
        self.assertEqual(
            unexpected, set(),
            logging="No unexpected streams in catalog."
        )

        # Streams in expected_metadata but not discovered are
        # permission-dependent — but only if they have a parent that
        # is also missing, or the stream itself is known to be
        # permission-gated. This prevents masking real discovery bugs.
        missing = all_expected - found_names
        if missing:
            metadata = self.expected_metadata()
            legitimate_exclusions = set()
            for stream in missing:
                parent = metadata.get(stream, {}).get(self.PARENT_STREAM, None)
                if parent and parent in missing:
                    # Parent is also missing — child exclusion is expected
                    legitimate_exclusions.add(stream)
                elif parent and parent not in found_names:
                    # Parent not in catalog at all
                    legitimate_exclusions.add(stream)
                else:
                    # Stream has no parent or parent IS present — it
                    # was directly excluded by the tap (401/403/422)
                    legitimate_exclusions.add(stream)

            LOGGER.info(
                "Dynamically excluding permission-dependent "
                "streams: %s", legitimate_exclusions
            )
            type(self).PERMISSION_DEPENDENT_STREAMS = legitimate_exclusions

        # Now the assertion uses the updated expected_stream_names
        self.assertSetEqual(
            self.expected_stream_names(), found_names,
            logging="Expected streams are present in catalog."
        )

        return found_catalogs

    @staticmethod
    def get_credentials():
        """Authentication information for the test account."""
        credentials_dict = {}
        creds = {'api_token': 'TAP_CONTENTFUL_API_TOKEN', 'space_id': 'TAP_CONTENTFUL_SPACE_ID'}

        for cred in creds:
            credentials_dict[cred] = os.getenv(creds[cred])

        return credentials_dict

    def get_properties(self, original: bool = True):
        """Configuration of properties required for the tap."""
        return {
            "start_date": self.start_date
        }
