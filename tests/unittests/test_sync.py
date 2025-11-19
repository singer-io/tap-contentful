import unittest
from unittest.mock import patch, MagicMock
from tap_contentful.sync import write_schema, sync, update_currently_syncing

class TestSync(unittest.TestCase):

    def test_write_schema_only_parent_selected(self):
        mock_stream = MagicMock()
        mock_stream.is_selected.return_value = True
        mock_stream.children = ["content_types", "assets"]
        mock_stream.child_to_sync = []

        client = MagicMock()
        catalog = MagicMock()
        catalog.get_stream.return_value = MagicMock()

        write_schema(mock_stream, client, [], catalog)

        mock_stream.write_schema.assert_called_once()
        self.assertEqual(len(mock_stream.child_to_sync), 0)

    def test_write_schema_parent_child_both_selected(self):
        mock_stream = MagicMock()
        mock_stream.is_selected.return_value = True
        mock_stream.children = ["content_types", "assets"]
        mock_stream.child_to_sync = []

        client = MagicMock()
        catalog = MagicMock()
        catalog.get_stream.return_value = MagicMock()

        write_schema(mock_stream, client, ["content_types"], catalog)

        mock_stream.write_schema.assert_called_once()
        self.assertEqual(len(mock_stream.child_to_sync), 1)

    def test_write_schema_child_selected(self):
        mock_stream = MagicMock()
        mock_stream.is_selected.return_value = False
        mock_stream.children = ["content_types", "assets"]
        mock_stream.child_to_sync = []

        client = MagicMock()
        catalog = MagicMock()
        catalog.get_stream.return_value = MagicMock()

        write_schema(mock_stream, client, ["content_types", "assets"], catalog)

        mock_stream.write_schema.assert_not_called()
        self.assertEqual(len(mock_stream.child_to_sync), 2)

    @patch("tap_contentful.streams.abstracts.BaseStream.get_records", return_value=[])
    @patch("tap_contentful.streams.abstracts.BaseStream.sync", new_callable=MagicMock)
    @patch("singer.write_schema")
    @patch("singer.get_currently_syncing")
    @patch("singer.Transformer")
    @patch("singer.write_state")
    def test_sync_stream1_called(
        self,
        mock_write_state,
        mock_transformer,
        mock_get_currently_syncing,
        mock_write_schema,
        mock_stream_sync,
        mock_get_records
    ):
        mock_catalog = MagicMock()
        state = {}
        client = MagicMock()
        config = {}

        invoice_stream = MagicMock()
        invoice_stream.stream = "content_types"
        expense_stream = MagicMock()
        expense_stream.stream = "assets"

        mock_catalog.get_selected_streams.return_value = [invoice_stream, expense_stream]

        sync(client, config, mock_catalog, state)

        self.assertEqual(mock_stream_sync.call_count, 0)

    @patch("tap_contentful.streams.abstracts.BaseStream.get_records", return_value=[])
    @patch("tap_contentful.streams.abstracts.BaseStream.sync", new_callable=MagicMock)
    @patch("singer.write_schema")
    @patch("singer.get_currently_syncing")
    @patch("singer.Transformer")
    @patch("singer.write_state")
    def test_sync_child_selected(
        self,
        mock_write_state,
        mock_transformer,
        mock_get_currently_syncing,
        mock_write_schema,
        mock_stream_sync,
        mock_get_records
    ):
        mock_catalog = MagicMock()
        state = {}
        client = MagicMock()
        config = {}

        child_stream1 = MagicMock()
        child_stream1.stream = "content_types"
        child_stream2 = MagicMock()
        child_stream2.stream = "assets"

        mock_catalog.get_selected_streams.return_value = [child_stream1, child_stream2]

        sync(client, config, mock_catalog, state)

        self.assertEqual(mock_stream_sync.call_count, 0)

    @patch("singer.get_currently_syncing")
    @patch("singer.set_currently_syncing")
    @patch("singer.write_state")
    def test_remove_currently_syncing(self, mock_write_state, mock_set_currently_syncing, mock_get_currently_syncing):
        mock_get_currently_syncing.return_value = "some_stream"
        state = {"currently_syncing": "some_stream"}

        update_currently_syncing(state, None)

        mock_get_currently_syncing.assert_called_once_with(state)
        mock_set_currently_syncing.assert_not_called()
        mock_write_state.assert_called_once_with(state)
        self.assertNotIn("currently_syncing", state)

    @patch("singer.get_currently_syncing")
    @patch("singer.set_currently_syncing")
    @patch("singer.write_state")
    def test_set_currently_syncing(self, mock_write_state, mock_set_currently_syncing, mock_get_currently_syncing):
        mock_get_currently_syncing.return_value = None
        state = {}

        update_currently_syncing(state, "new_stream")

        mock_get_currently_syncing.assert_not_called()
        mock_set_currently_syncing.assert_called_once_with(state, "new_stream")
        mock_write_state.assert_called_once_with(state)
        self.assertNotIn("currently_syncing", state)
