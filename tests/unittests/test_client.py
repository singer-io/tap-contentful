import unittest
import requests
from unittest.mock import patch
from parameterized import parameterized
from requests.exceptions import Timeout, ConnectionError, ChunkedEncodingError
from tap_contentful.client import Client
from tap_contentful.exceptions import *


default_config = {
    "base_url": "https://api.example.com",
    "request_timeout": 30,
    "api_token": "dummy_token",
}

DEFAULT_REQUEST_TIMEOUT = 300

class MockResponse:
    """Mocked standard HTTPResponse to test error handling."""

    def __init__(
        self, status_code, resp = "", content=[""], headers=None, raise_error=True, text={}
    ):
        self.json_data = resp
        self.status_code = status_code
        self.content = content
        self.headers = headers
        self.raise_error = raise_error
        self.text = text
        self.reason = "error"

    def raise_for_status(self):
        """If an error occur, this method returns a HTTPError object.

        Raises:
            requests.HTTPError: Mock http error.

        Returns:
            int: Returns status code if not error occurred.
        """
        if not self.raise_error:
            return self.status_code

        raise requests.HTTPError("mock sample message")

    def json(self):
        """Returns a JSON object of the result."""
        return self.text

class TestClient(unittest.TestCase):

    def setUp(self):
        """Set up the client with default configuration."""
        self.client = Client(default_config)

    @parameterized.expand([
        ["empty value", "", DEFAULT_REQUEST_TIMEOUT],
        ["string value", "12", 12.0],
        ["integer value", 10, 10.0],
        ["float value", 20.0, 20.0],
        ["zero value", 0, DEFAULT_REQUEST_TIMEOUT]
    ])
    @patch("tap_contentful.client.session")
    def test_client_initialization(self, test_name, input_value, expected_value, mock_session):
        default_config["request_timeout"] = input_value
        client = Client(default_config)
        assert client.request_timeout == expected_value
        assert isinstance(client._session, mock_session().__class__)



    @parameterized.expand([
        ["400 error", 400, MockResponse(400), contentfulBadRequestError, "A validation exception has occurred."],
        ["401 error", 401, MockResponse(401), contentfulUnauthorizedError, "The access token provided is expired, revoked, malformed or invalid for other reasons."],
        ["403 error", 403, MockResponse(403), contentfulForbiddenError, "You are missing the following required scopes: read"],
        ["404 error", 404, MockResponse(404), contentfulNotFoundError, "The resource you have specified cannot be found."],
        ["409 error", 409, MockResponse(409), contentfulConflictError, "The API request cannot be completed because the requested operation would conflict with an existing item."],
        ["422 error", 422, MockResponse(422), contentfulUnprocessableEntityError, "The request content itself is not processable by the server."],
    ])
    def test_make_request_http_failure_without_retry(self, test_name, error_code, mock_response, error, error_message):

        with patch.object(self.client._session, "request", return_value=mock_response) as mock_request:
            with self.assertRaises(error) as e:
                self.client._Client__make_request("GET", "https://api.example.com/resource")

        expected_error_message = (f"HTTP-error-code: {error_code}, Error: {error_message}")
        self.assertEqual(str(e.exception), expected_error_message)
        self.assertEqual(mock_request.call_count, 1)

    @parameterized.expand([
        ["429 error", 429, MockResponse(429), contentfulRateLimitError, "The API rate limit for your organisation/application pairing has been exceeded. (Retry after 60 seconds.)"],
        ["500 error", 500, MockResponse(500), contentfulInternalServerError, "The server encountered an unexpected condition which prevented it from fulfilling the request."],
        ["502 error", 502, MockResponse(502), contentfulBadGatewayError, "Server received an invalid response."],
    ])
    @patch("time.sleep")
    def test_make_request_http_failure_with_retry(self, test_name, error_code, mock_response, error, error_message, mock_sleep):

        with patch.object(self.client._session, "request", return_value=mock_response) as mock_request:
            with self.assertRaises(error) as e:
                self.client._Client__make_request("GET", "https://api.example.com/resource")

            expected_error_message = (f"HTTP-error-code: {error_code}, Error: {error_message}")
            self.assertEqual(str(e.exception), expected_error_message)
            self.assertEqual(mock_request.call_count, 5)

    @parameterized.expand([
        ["ConnectionResetError", ConnectionResetError],
        ["ConnectionError", ConnectionError],
        ["ChunkedEncodingError", ChunkedEncodingError],
        ["Timeout", Timeout],
    ])
    @patch("time.sleep")
    def test_make_request_other_failure_with_retry(self, test_name, error, mock_sleep):

        with patch.object(self.client._session, "request", side_effect=error) as mock_request:
            with self.assertRaises(error) as e:
                self.client._Client__make_request("GET", "https://api.example.com/resource")

            self.assertEqual(mock_request.call_count, 5)

    @parameterized.expand([
        ["503 error - Service Unavailable", 503, "Unknown Error"],
        ["504 error - Gateway Timeout", 504, "Unknown Error"],
        ["505 error - HTTP Version Not Supported", 505, "Unknown Error"],
        ["506 error - Variant Also Negotiates", 506, "Unknown Error"],
        ["507 error - Insufficient Storage", 507, "Unknown Error"],
        ["508 error - Loop Detected", 508, "Unknown Error"],
        ["509 error - Bandwidth Limit Exceeded", 509, "Unknown Error"],
        ["510 error - Not Extended", 510, "Unknown Error"],
        ["511 error - Network Authentication Required", 511, "Unknown Error"],
    ])
    @patch("time.sleep")
    def test_unmapped_5xx_errors_trigger_backoff(self, test_name, error_code, error_message, mock_sleep):
        """Test that unmapped 5xx errors trigger backoff retry as contentfulBackoffError."""
        mock_response = MockResponse(error_code)

        with patch.object(self.client._session, "request", return_value=mock_response) as mock_request:
            with self.assertRaises(contentfulBackoffError) as e:
                self.client._Client__make_request("GET", "https://api.example.com/resource")

            expected_error_message = f"HTTP-error-code: {error_code}, Error: {error_message}"
            self.assertEqual(str(e.exception), expected_error_message)
            # Verify backoff retry happened - should retry 5 times
            self.assertEqual(mock_request.call_count, 5)
