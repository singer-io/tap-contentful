from tap_contentful.streams.environments import Environments
from tap_contentful.streams.organizations import Organizations
from tap_contentful.streams.security_contacts import SecurityContacts
from tap_contentful.streams.content_types import ContentTypes
from tap_contentful.streams.environment_templates import EnvironmentTemplates
from tap_contentful.streams.entries import Entries
from tap_contentful.streams.assets import Assets
from tap_contentful.streams.locales import Locales
from tap_contentful.streams.taxonomy_concepts import TaxonomyConcepts
from tap_contentful.streams.tags import Tags
from tap_contentful.streams.tasks import Tasks

STREAMS = {
    "environments": Environments,
    "organizations": Organizations,
    "security_contacts": SecurityContacts,
    "content_types": ContentTypes,
    "environment_templates": EnvironmentTemplates,
    "entries": Entries,
    "assets": Assets,
    "locales": Locales,
    "taxonomy_concepts": TaxonomyConcepts,
    "tags": Tags,
    "tasks": Tasks,
}

