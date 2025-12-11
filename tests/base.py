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
                cls.PRIMARY_KEYS: { "id", "space_id" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "organizations": {
                cls.PRIMARY_KEYS: { "id" },
                cls.REPLICATION_METHOD: cls.FULL_TABLE,
                cls.REPLICATION_KEYS: set(),
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100
            },
            "security_contacts": {
                cls.PRIMARY_KEYS: { "id", "organization_id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "organizations"
            },
            "content_types": {
                cls.PRIMARY_KEYS: { "id","space_id", "environment_id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "environment_templates": {
                cls.PRIMARY_KEYS: { "id", "organization_id"},
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "organizations"
            },
            "entries": {
                cls.PRIMARY_KEYS: { "id", "space_id", "environment_id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "assets": {
                cls.PRIMARY_KEYS: { "id", "space_id", "environment_id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "locales": {
                cls.PRIMARY_KEYS: { "id", "space_id", "environment_id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "taxonomy_concepts": {
                cls.PRIMARY_KEYS: { "id", "organization_id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "organizations"
            },
            "tags": {
                cls.PRIMARY_KEYS: { "id", "space_id", "environment_id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            },
            "tasks": {
                cls.PRIMARY_KEYS: { "id", "space_id", "environment_id" },
                cls.REPLICATION_METHOD: cls.INCREMENTAL,
                cls.REPLICATION_KEYS: { "updatedAt" },
                cls.OBEYS_START_DATE: False,
                cls.API_LIMIT: 100,
                cls.PARENT_STREAM: "environments"
            }
        }

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
