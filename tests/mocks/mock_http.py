"""
Mock implementation of HTTP requests for testing.

This module mocks the requests library to allow testing of code that makes HTTP requests
without actually making network calls.
"""


import json
import re
from typing import Any, Callable, Dict, Iterator, List, Optional, Union
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlparse

from requests.exceptions import HTTPError


class MockResponse:
    """Mock implementation of a requests.Response object."""

    def __init__(
        self,
        status_code: int = 200,
        content: Union[bytes, str] = b"",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        url: str = "https://mock-url.com",
        reason: str = "OK",
        encoding: str = "utf-8",
        cookies: Optional[Dict[str, str]] = None,
        elapsed: float = 0.1,
        request: Optional[Any] = None,
    ):
        """
        Initialize a mock response.

        Args:
            status_code: HTTP status code
            content: Response content as bytes or string
            headers: Response headers
            json_data: Response data to return as JSON
            url: URL that was requested
            reason: Status reason phrase
            encoding: Response encoding
            cookies: Response cookies
            elapsed: Time elapsed in seconds
            request: Original request object
        """
        self.status_code = status_code
        self._content = content.encode("utf-8") if isinstance(content, str) else content
        self.headers = headers or {}
        self._json_data = json_data
        self.url = url
        self.reason = reason
        self.encoding = encoding
        self.cookies = cookies or {}
        self.elapsed = MagicMock()
        self.elapsed.total_seconds.return_value = elapsed
        self.request = request
        self._iter_content_index = 0

        # Set Content-Length header if not present and content exists
        if "content-length" not in self.headers and self._content:
            self.headers["content-length"] = str(len(self._content))

        # Set encoding based on headers if not specified
        if (
            "content-type" in self.headers
            and "charset=" in self.headers["content-type"]
        ):
            charset_match = re.search(
                r"charset=([^\s;]+)", self.headers["content-type"]
            )
            if charset_match:
                self.encoding = charset_match.group(1)

    @property
    def content(self) -> bytes:
        """Get the raw content of the response."""
        return self._content

    @property
    def text(self) -> str:
        """Get the decoded content of the response."""
        return self._content.decode(self.encoding)

    def json(self) -> Any:
        """Parse the response as JSON."""
        if self._json_data is not None:
            return self._json_data
        return json.loads(self.text)

    def iter_content(self, chunk_size: int = 1) -> Iterator[bytes]:
        """
        Iterate through the content in chunks.

        Args:
            chunk_size: Size of chunks to yield

        Yields:
            Content chunks
        """
        for i in range(0, len(self._content), chunk_size):
            yield self._content[i : i + chunk_size]

    def raise_for_status(self) -> None:
        """Raise an exception if the status code indicates an error."""
        if 400 <= self.status_code < 600:
            from requests.exceptions import HTTPError
            raise HTTPError(f"{self.status_code} {self.reason}", response=self)


class MockSession(MagicMock):
    """Mock implementation of a requests.Session object."""

    def __init__(self, *args, **kwargs):
        """Initialize a mock session."""
        super().__init__(*args, **kwargs)
        self._request_history = []

    def get_request_history(self) -> List[Dict[str, Any]]:
        """Get the history of requests made through this session."""
        return self._request_history

    def request(self, method: str, url: str, **kwargs) -> MockResponse:
        """
        Make a request through the session.

        Args:
            method: HTTP method
            url: URL to request
            **kwargs: Additional arguments to pass to the request

        Returns:
            Mock response
        """
        # Record the request
        request_info = {"method": method, "url": url, "kwargs": kwargs}
        self._request_history.append(request_info)

        # Call the parent method
        return super().request(method, url, **kwargs)


class MockRequests:
    """
    Mock implementation of the requests library.

    This class mocks the requests library to allow testing of code that makes HTTP requests
    without actually making network calls.
    """

    def __init__(self):
        """Initialize the mock requests library."""
        self.responses = {}
        self.sessions = {}
        self.request_history = []

        # Create methods that match the requests library's API
        self.get = self._create_method("GET")
        self.post = self._create_method("POST")
        self.put = self._create_method("PUT")
        self.delete = self._create_method("DELETE")
        self.patch = self._create_method("PATCH")
        self.head = self._create_method("HEAD")
        self.options = self._create_method("OPTIONS")

    def _create_method(self, method: str) -> Callable:
        """
        Create a method that matches the requests library's API.

        Args:
            method: HTTP method

        Returns:
            Function that makes a request
        """

        def request_method(url: str, **kwargs) -> MockResponse:
            return self.request(method, url, **kwargs)

        return request_method

    def request(self, method: str, url: str, **kwargs) -> MockResponse:
        """
        Make a request.

        Args:
            method: HTTP method
            url: URL to request
            **kwargs: Additional arguments to pass to the request

        Returns:
            Mock response
        """
        # Record the request
        request_info = {"method": method, "url": url, "kwargs": kwargs}
        self.request_history.append(request_info)

        # Parse the URL
        parsed_url = urlparse(url)
        parse_qs(parsed_url.query)

        # Find a matching response pattern
        response = None
        for pattern, resp_factory in self.responses.items():
            # Check if the pattern matches the URL
            if isinstance(pattern, str):
                if self._url_matches_pattern(url, pattern):
                    if callable(resp_factory):
                        response = resp_factory(method, url, **kwargs)
                    else:
                        response = resp_factory
                    break
            # Check if the pattern is a tuple of (method, url_pattern)
            elif isinstance(pattern, tuple) and len(pattern) == 2:
                req_method, url_pattern = pattern
                if method == req_method and self._url_matches_pattern(url, url_pattern):
                    if callable(resp_factory):
                        response = resp_factory(method, url, **kwargs)
                    else:
                        response = resp_factory
                    break

        # If no match found, return a default response
        if response is None:
            # Create a default response
            response = MockResponse(
                status_code=404,
                content=f"No mock response found for {method} {url}",
                headers={"Content-Type": "text/plain"},
                url=url,
                reason="Not Found",
            )

        return response

    def _url_matches_pattern(self, url: str, pattern: str) -> bool:
        """
        Check if a URL matches a pattern.

        Args:
            url: URL to check
            pattern: Pattern to match against

        Returns:
            True if the URL matches the pattern, False otherwise
        """
        # If the pattern is an exact match, return True
        if url == pattern:
            return True

        # If the pattern is a regex pattern, check if it matches
        if pattern.startswith("^") or pattern.endswith("$"):
            return bool(re.match(pattern, url))

        # Otherwise, check if the pattern is a substring of the URL
        return pattern in url

    def add_response(
        self,
        url_pattern: Union[str, tuple],
        response: Union[MockResponse, Dict[str, Any], bytes, str, Callable],
        method: Optional[str] = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Add a mock response for a URL pattern.

        Args:
            url_pattern: URL pattern to match
            response: Response to return
            method: HTTP method to match (if not included in url_pattern)
            status_code: Status code to return (if response is not a MockResponse)
            headers: Headers to include in the response (if response is not a MockResponse)
        """
        # If method is provided separately, create a tuple pattern
        pattern = url_pattern
        if isinstance(url_pattern, str) and method is not None:
            pattern = (method, url_pattern)

        # If response is not a MockResponse, convert it
        if not isinstance(response, MockResponse):
            if callable(response):
                # If response is a callable, keep it as is
                self.responses[pattern] = response
                return

            # Convert the response to a MockResponse
            if isinstance(response, (dict, list)):
                # Convert to JSON
                headers = headers or {"Content-Type": "application/json"}
                self.responses[pattern] = MockResponse(
                    status_code=status_code, json_data=response, headers=headers
                )
            elif isinstance(response, bytes):
                # Use as raw bytes
                self.responses[pattern] = MockResponse(
                    status_code=status_code, content=response, headers=headers
                )
            elif isinstance(response, str):
                # Use as text
                headers = headers or {"Content-Type": "text/plain"}
                self.responses[pattern] = MockResponse(
                    status_code=status_code, content=response, headers=headers
                )
            else:
                # Convert to string
                headers = headers or {"Content-Type": "text/plain"}
                self.responses[pattern] = MockResponse(
                    status_code=status_code, content=str(response), headers=headers
                )
        else:
            # Use the MockResponse as is
            self.responses[pattern] = response

    def reset(self) -> None:
        """Reset the mock requests library."""
        self.responses = {}
        self.sessions = {}
        self.request_history = []

    def session(self) -> MockSession:
        """Create a new session."""
        session = MockSession()
        session_id = id(session)
        self.sessions[session_id] = session
        return session


# Create a mock requests module
mock_requests = MockRequests()


# Example usage
if __name__ == "__main__":
    # Add a mock response for a URL pattern
    mock_requests.add_response(
        "https://api.example.com/users",
        [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
    )

    # Make a request
    response = mock_requests.get("https://api.example.com/users")

    # Get the response data
    data = response.json()

    print(f"Status code: {response.status_code}")
    print(f"Data: {data}")
    print(f"Request history: {mock_requests.request_history}")