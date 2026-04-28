import unittest
from unittest.mock import MagicMock, patch

from tap_contentful.discover import (
    discover,
    is_stream_available,
    _get_probe_url,
    _resolve_org_probe_urls,
    _get_unavailable_streams,
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


class TestGetUnavailableStreams(unittest.TestCase):

    @patch("tap_contentful.discover.STREAMS", {
        "organizations": type("S", (), {
            "path": "/organizations",
            "parent": "",
        }),
        "security_contacts": type("S", (), {
            "path": "/organizations/{organization_id}/security_contacts",
            "parent": "organizations",
        }),
        "taxonomy_concepts": type("S", (), {
            "path": "/organizations/{organization_id}/taxonomy_concepts",
            "parent": "organizations",
        }),
    })
    def test_org_children_excluded_when_org_unavailable(self):
        """Test that org-child streams are excluded when organizations endpoint is forbidden."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}
        # /organizations returns 403 — so _resolve_org_probe_urls returns empty
        client.make_request.side_effect = contentfulForbiddenError("Forbidden")

        unavailable = _get_unavailable_streams(client)

        # organizations itself returns 403 during probing
        self.assertIn("organizations", unavailable)
        # Children can't be probed (no org ID) — should also be excluded
        self.assertIn("security_contacts", unavailable)
        self.assertIn("taxonomy_concepts", unavailable)

    @patch("tap_contentful.discover.STREAMS", {
        "organizations": type("S", (), {
            "path": "/organizations",
            "parent": "",
        }),
        "environment_templates": type("S", (), {
            "path": "/organizations/{organization_id}/environment_templates",
            "parent": "organizations",
        }),
        "environments": type("S", (), {
            "path": "/spaces/{space_id}/environments",
            "parent": "",
        }),
    })
    def test_parent_unavailable_excludes_children(self):
        """Test that when a parent stream is probed and unavailable,
        its children are excluded in the second pass."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}

        def mock_request(method, url, params=None, headers=None):
            if "/organizations" in url and "environment_templates" not in url:
                # organizations endpoint accessible, returns an org
                if params and params.get("limit") == 1:
                    return {"items": [{"sys": {"id": "org-1"}}]}
                raise contentfulForbiddenError("Forbidden")
            if "environment_templates" in url:
                return {"items": []}  # accessible
            if "environments" in url:
                return {"items": []}
            return {"items": []}

        client.make_request.side_effect = mock_request

        unavailable = _get_unavailable_streams(client)

        # organizations probed OK (returns items for limit=1)
        # environment_templates probed OK
        # environments probed OK
        self.assertEqual(unavailable, set())

    @patch("tap_contentful.discover.STREAMS", {
        "environments": type("S", (), {
            "path": "/spaces/{space_id}/environments",
            "parent": "",
        }),
        "content_types": type("S", (), {
            "path": "/spaces/{space_id}/environments/{environment_id}/content_types",
            "parent": "environments",
        }),
        "entries": type("S", (), {
            "path": "/spaces/{space_id}/environments/{environment_id}/entries",
            "parent": "environments",
        }),
    })
    def test_parent_environments_unavailable_excludes_children(self):
        """Test that when environments is unavailable, its children are excluded."""
        client = MagicMock()
        client.base_url = "https://api.contentful.com"
        client.config = {"space_id": "abc123"}

        def mock_request(method, url, params=None, headers=None):
            if "environments" in url and "content_types" not in url and "entries" not in url:
                raise contentfulForbiddenError("Forbidden")
            return {"items": []}

        client.make_request.side_effect = mock_request

        unavailable = _get_unavailable_streams(client)

        self.assertIn("environments", unavailable)
        # Children should be excluded because parent is unavailable
        self.assertIn("content_types", unavailable)
        self.assertIn("entries", unavailable)



