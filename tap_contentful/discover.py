import singer
from singer import metadata
from singer.catalog import Catalog, CatalogEntry, Schema

from tap_contentful.exceptions import (
    contentfulForbiddenError,
    contentfulUnauthorizedError,
    contentfulUnprocessableEntityError,
)
from tap_contentful.client import Client
from tap_contentful.schema import get_schemas
from tap_contentful.streams import STREAMS

LOGGER = singer.get_logger()

# Exceptions that indicate a stream is not available for this account
_STREAM_UNAVAILABLE_EXCEPTIONS = (
    contentfulUnauthorizedError,
    contentfulForbiddenError,
    contentfulUnprocessableEntityError,
)


def _get_probe_url(client, stream_cls):
    """
    Build a probe URL for a stream, resolving path parameters from the client config.
    Returns None if the URL cannot be resolved (e.g. missing parent IDs).
    Org-child streams (paths with organization_id) are handled by _get_org_probe_urls.
    """
    path = getattr(stream_cls, 'path', '')
    if not path:
        return None

    # Org-child paths are resolved separately via _get_org_probe_urls
    if '{organization_id}' in path or '{organizationId}' in path:
        return None

    space_id = client.config.get('space_id', '')
    # For child streams under environments, use 'master' as default environment
    try:
        url = f"{client.base_url}{path}".format(
            space_id=space_id,
            environment_id='master',
        )
    except (KeyError, IndexError):
        return None

    return url


def _get_org_probe_urls(client:Client):
    """
    Fetch the first organization ID and return resolved probe URLs for org-child streams.
    Returns a dict of {stream_name: probe_url}.
    """
    probe_urls = {}
    org_id = None

    # Fetch first org ID
    try:
        response = client.make_request(
            "GET", f"{client.base_url}/organizations",
            params={"limit": 1}, headers={}
        )
        items = response.get("items", [])
        if items:
            org_id = items[0].get("sys", {}).get("id")
    except _STREAM_UNAVAILABLE_EXCEPTIONS:
        pass

    if not org_id:
        return probe_urls

    for stream_name, stream_cls in STREAMS.items():
        parent = getattr(stream_cls, 'parent', '')
        if parent != 'organizations':
            continue
        path = getattr(stream_cls, 'path', '')
        try:
            url = f"{client.base_url}{path}".format(
                organization_id=org_id,
                organizationId=org_id,
            )
            probe_urls[stream_name] = url
        except (KeyError, IndexError):
            pass

    return probe_urls


def is_stream_available(client, stream_name, probe_url):
    """
    Probe a stream's API endpoint to check if it is available.
    Returns False if the API returns 401, 403, or 422 indicating the stream
    is unauthorized or requires a feature not configured in the account.
    """
    try:
        client.make_request("GET", probe_url, params={"limit": 1}, headers={})
        return True
    except _STREAM_UNAVAILABLE_EXCEPTIONS as e:
        LOGGER.warning(
            "Excluding stream '%s' from catalog: %s. "
            "This stream is not available for the current Contentful account.",
            stream_name, e.message,
        )
        return False


def _get_unavailable_streams(client:Client):
    """
    Probe all stream endpoints and return the set of stream names that are unavailable.

    Parent streams are probed first. If a parent is unavailable, all its children
    are excluded immediately without probing, to avoid unnecessary API calls.
    """
    unavailable = set()

    # Resolve org-child probe URLs (requires fetching an org ID first)
    org_child_urls = _get_org_probe_urls(client)

    # First pass: probe parent streams only (streams with no parent)
    for stream_name, stream_cls in STREAMS.items():
        parent = getattr(stream_cls, 'parent', '')
        if parent:
            continue  # Skip child streams in first pass

        probe_url = _get_probe_url(client, stream_cls)
        if not probe_url:
            continue

        if not is_stream_available(client, stream_name, probe_url):
            unavailable.add(stream_name)

    # Second pass: probe child streams, skipping those whose parent is unavailable
    for stream_name, stream_cls in STREAMS.items():
        parent = getattr(stream_cls, 'parent', '')
        if not parent:
            continue  # Skip parent streams (already handled)

        # If parent is unavailable, exclude child without probing
        if parent in unavailable:
            LOGGER.warning(
                "Excluding child stream '%s' because parent stream '%s' is unavailable.",
                stream_name, parent,
            )
            unavailable.add(stream_name)
            continue

        if parent == 'organizations':
            probe_url = org_child_urls.get(stream_name)
            if not probe_url:
                LOGGER.warning(
                    "Excluding child stream '%s': unable to resolve probe URL "
                    "(parent 'organizations' may be unavailable).",
                    stream_name,
                )
                unavailable.add(stream_name)
                continue
        else:
            probe_url = _get_probe_url(client, stream_cls)
            if not probe_url:
                continue

        if not is_stream_available(client, stream_name, probe_url):
            unavailable.add(stream_name)

    return unavailable


def discover(client: Client) -> Catalog:
    """
    Run the discovery mode, prepare the catalog file and return the catalog.
    """
    schemas, field_metadata = get_schemas()
    catalog = Catalog([])

    unavailable = _get_unavailable_streams(client)

    for stream_name, schema_dict in schemas.items():
        if stream_name in unavailable:
            continue

        try:
            schema = Schema.from_dict(schema_dict)
            mdata = field_metadata[stream_name]
        except Exception as err:
            LOGGER.error(err)
            LOGGER.error("stream_name: {}".format(stream_name))
            LOGGER.error("type schema_dict: {}".format(type(schema_dict)))
            raise err

        key_properties = metadata.to_map(mdata).get((), {}).get("table-key-properties")

        catalog.streams.append(
            CatalogEntry(
                stream=stream_name,
                tap_stream_id=stream_name,
                key_properties=key_properties,
                schema=schema,
                metadata=mdata,
            )
        )

    return catalog
