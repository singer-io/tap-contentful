class contentfulError(Exception):
    """class representing Generic Http error."""

    def __init__(self, message=None, response=None):
        super().__init__(message)
        self.message = message
        self.response = response


class contentfulBackoffError(contentfulError):
    """class representing backoff error handling."""
    pass

class contentfulBadRequestError(contentfulError):
    """class representing 400 status code."""
    pass

class contentfulUnauthorizedError(contentfulError):
    """class representing 401 status code."""
    pass


class contentfulForbiddenError(contentfulError):
    """class representing 403 status code."""
    pass

class contentfulNotFoundError(contentfulError):
    """class representing 404 status code."""
    pass

class contentfulConflictError(contentfulError):
    """class representing 409 status code."""
    pass

class contentfulUnprocessableEntityError(contentfulBackoffError):
    """class representing 422 status code."""
    pass

class contentfulRateLimitError(contentfulBackoffError):
    """class representing 429 status code."""
    def __init__(self, message=None, response=None):
        """
        Initialize the contentful_RateLimitError.
        Sets the `retry_after` attribute from the 'X-Contentful-RateLimit-Reset' header if available.
        """
        self.response = response

        # Use 'X-Contentful-RateLimit-Reset' header or fallback to 60 seconds
        if response and hasattr(response, 'headers') and response.headers:
            self.retry_after = int(response.headers.get('X-Contentful-RateLimit-Reset', 60))
        else:
            self.retry_after = 60

        base_msg = message or "Rate limit hit"
        retry_info = f"(Retry after {self.retry_after} seconds.)"
        full_message = f"{base_msg} {retry_info}"
        super().__init__(full_message, response=response)

class contentfulInternalServerError(contentfulBackoffError):
    """class representing 500 status code."""
    pass

class contentfulNotImplementedError(contentfulBackoffError):
    """class representing 501 status code."""
    pass

class contentfulBadGatewayError(contentfulBackoffError):
    """class representing 502 status code."""
    pass

class contentfulServiceUnavailableError(contentfulBackoffError):
    """class representing 503 status code."""
    pass

class contentfulGatewayTimeoutError(contentfulBackoffError):
    """class representing 504 status code."""
    pass

ERROR_CODE_EXCEPTION_MAPPING = {
    400: {
        "raise_exception": contentfulBadRequestError,
        "message": "A validation exception has occurred."
    },
    401: {
        "raise_exception": contentfulUnauthorizedError,
        "message": "The access token provided is expired, revoked, malformed or invalid for other reasons."
    },
    403: {
        "raise_exception": contentfulForbiddenError,
        "message": "You are missing the following required scopes: read"
    },
    404: {
        "raise_exception": contentfulNotFoundError,
        "message": "The resource you have specified cannot be found."
    },
    409: {
        "raise_exception": contentfulConflictError,
        "message": "The API request cannot be completed because the requested operation would conflict with an existing item."
    },
    422: {
        "raise_exception": contentfulUnprocessableEntityError,
        "message": "The request content itself is not processable by the server."
    },
    429: {
        "raise_exception": contentfulRateLimitError,
        "message": "The API rate limit for your organisation/application pairing has been exceeded."
    },
    500: {
        "raise_exception": contentfulInternalServerError,
        "message": "The server encountered an unexpected condition which prevented" \
            " it from fulfilling the request."
    },
    501: {
        "raise_exception": contentfulNotImplementedError,
        "message": "The server does not support the functionality required to fulfill the request."
    },
    502: {
        "raise_exception": contentfulBadGatewayError,
        "message": "Server received an invalid response."
    },
    503: {
        "raise_exception": contentfulServiceUnavailableError,
        "message": "API service is currently unavailable."
    },
    504: {
        "raise_exception": contentfulGatewayTimeoutError,
        "message": "The server did not receive a timely response from an upstream server."
    }
}
