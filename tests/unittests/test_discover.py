import unittest
from unittest.mock import MagicMock, patch

from tap_contentful.discover import (
    discover,
    is_stream_available,
    _get_probe_url,
    _resolve_org_probe_urls,
    _check_connectivity,
)
from tap_contentful.exceptions import (
    contentfulForbiddenError,
    contentfulUnauthorizedError,
    contentfulUnprocessableEntityError,
)


class TestDiscover(unittest.TestCase):
    test_stream_name = "test"

    dummy_schema = {
        test_stream_name: {
            "type": "object",
            "properties": {
                "id": {
                    "type": [
                        "null",
                        "string"
                    ]
                },
            }
        }
    }

    dummy_metadata = {
        test_stream_name: {
            (): {
                "breadcrumb": (),
                "table-key-properties": ["id"],
                "forced-replication-method": "FULL_TABLE",
                "valid-replication-keys": [],
            }
        }
    }

    @patch("tap_contentful.discover.get_schemas")
    @patch("singer.metadata.to_map")
    def test_discover(self, mock_to_map, mock_get_schemas):
        """Test the discover function without client (backward compatible)."""
        mock_get_schemas.return_value = (self.dummy_schema, self.dummy_metadata)
        mock_to_map.return_value = self.dummy_metadata[self.test_stream_name]

        catalog_obj = discover()

        self.assertIsNotNone(catalog_obj)
        self.assertEqual(len(catalog_obj.streams), 1)
        self.assertEqual(catalog_obj.streams[0].stream, self.test_stream_name)

    @patch("tap_contentful.discover._get_unavailable_streams")
    @patch("tap_contentful.discover.get_schemas")
    @patch("singer.metadata.to_map")
    def test_discover_excludes_unavailable_streams(self, mock_to_map, mock_get_schemas, mock_unavailable):
        """Test that discover excludes streams that are unavailable."""
        schemas = {
            "available_stream": self.dummy_schema[self.test_stream_name],
            "unavailable_stream": self.dummy_schema[self.test_stream_name],
        }
        field_metadata = {
            "available_stream": self.dummy_metadata[self.test_stream_name],
            "unavailable_stream": self.dummy_metadata[self.test_stream_name],
        }
        mock_get_schemas.return_value = (schemas, field_metadata)
        mock_to_map.return_value = self.dummy_metadata[self.test_stream_name]
        mock_unavailable.return_value = {"unavailable_stream"}

        client = MagicMock()
        catalog_obj = discover(client=client)

        self.assertEqual(len(catalog_obj.streams), 1)
        self.assertEqual(catalog_obj.streams[0].stream, "available_stream")

    def test_discovery_error(self):
        """Test the discover function error handling."""
        with patch("tap_contentful.discover.get_schemas") as mock_get_schemas:
            mock_get_schemas.return_value = ({"invalid_stream": "invalid_schema"}, {})

            with self.assertRaises(Exception):
                discover()


class TestIsStreamAvailable(unittest.TestCase):

    def test_available_stream(self):
        """Test that a stream returning 200 is available."""
        client = MagicMock()
        client.make_request.return_value = {"items": []}

        self.assertTrue(is_stream_available(client, "my_stream", "https://api.contentful.com/test"))

    def test_unavailable_stream_403(self):
        """Test that a stream returning 403 is excluded."""
        client = MagicMock()
        client.make_request.side_effect = contentfulForbiddenError("Forbidden")

        self.assertFalse(is_stream_available(client, "my_stream", "https://api.contentful.com/test"))

    def test_unavailable_stream_401(self):
        """Test that a stream returning 401 is excluded."""
        client = MagicMock()
        client.make_request.side_effect = contentfulUnauthorizedError("Unauthorized")

        self.assertFalse(is_stream_available(client, "my_stream", "https://api.contentful.com/test"))

    def test_unavailable_stream_422(self):
        """Test that a stream returning 422 is excluded."""
        client = MagicMock()
        client.make_request.side_effect = contentfulUnprocessableEntityError("Unprocessable")

        self.assertFalse(is_stream_available(client, "my_stream", "https://api.contentful.com/test"))


class TestGetProbeUrl(unittest.TestCase):

    def test_simple_path(self):
        """Test probe URL for stream with no path params."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}
        stream_cls = type("S", (), {"path": "/organizations"})

        url = _get_probe_url(client, stream_cls)
        self.assertEqual(url, "https://api.contentful.com/organizations")

    def test_space_path(self):
        """Test probe URL for stream with space_id param."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}
        stream_cls = type("S", (), {"path": "/spaces/{space_id}/environments"})

        url = _get_probe_url(client, stream_cls)
        self.assertEqual(url, "https://api.contentful.com/spaces/abc123/environments")

    def test_environment_path(self):
        """Test probe URL for stream with space_id and environment_id."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}
        stream_cls = type("S", (), {"path": "/spaces/{space_id}/environments/{environment_id}/entries"})

        url = _get_probe_url(client, stream_cls)
        self.assertEqual(url, "https://api.contentful.com/spaces/abc123/environments/master/entries")

    def test_no_path(self):
        """Test that stream with no path returns None."""
        client = MagicMock()
        client.config = {"space_id": "abc123"}
        stream_cls = type("S", (), {"path": ""})

        url = _get_probe_url(client, stream_cls)
        self.assertIsNone(url)


class TestResolveOrgProbeUrls(unittest.TestCase):

    @patch("tap_contentful.discover.STREAMS", {
        "environment_templates": type("S", (), {
            "path": "/organizations/{organization_id}/environment_templates",
            "parent": "organizations",
        }),
        "organizations": type("S", (), {
            "path": "/organizations",
            "parent": "",
        }),
    })
    def test_resolves_org_child_urls(self):
        """Test that org-child URLs are resolved with real org ID."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.make_request.return_value = {
            "items": [{"sys": {"id": "org-123"}}]
        }

        urls = _resolve_org_probe_urls(client)

        self.assertIn("environment_templates", urls)
        self.assertIn("org-123", urls["environment_templates"])

    @patch("tap_contentful.discover.STREAMS", {
        "environment_templates": type("S", (), {
            "path": "/organizations/{organization_id}/environment_templates",
            "parent": "organizations",
        }),
    })
    def test_returns_empty_when_no_orgs(self):
        """Test that empty dict is returned when no organizations exist."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.make_request.return_value = {"items": []}

        urls = _resolve_org_probe_urls(client)

        self.assertEqual(urls, {})

    @patch("tap_contentful.discover.STREAMS", {
        "environment_templates": type("S", (), {
            "path": "/organizations/{organization_id}/environment_templates",
            "parent": "organizations",
        }),
    })
    def test_returns_empty_when_orgs_forbidden(self):
        """Test that empty dict is returned when organizations endpoint returns 403."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.make_request.side_effect = contentfulForbiddenError("Forbidden")

        urls = _resolve_org_probe_urls(client)

        self.assertEqual(urls, {})


class TestCheckConnectivity(unittest.TestCase):

    def test_returns_true_when_space_accessible(self):
        """Test connectivity passes when space endpoint returns 200."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}
        client.make_request.return_value = {"items": []}

        self.assertTrue(_check_connectivity(client))

    def test_returns_false_on_forbidden(self):
        """Test connectivity fails when space endpoint returns 403."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}
        client.make_request.side_effect = contentfulForbiddenError(
            "Forbidden"
        )

        self.assertFalse(_check_connectivity(client))

    def test_returns_false_on_unauthorized(self):
        """Test connectivity fails when space endpoint returns 401."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}
        client.make_request.side_effect = contentfulUnauthorizedError(
            "Unauthorized"
        )

        self.assertFalse(_check_connectivity(client))
