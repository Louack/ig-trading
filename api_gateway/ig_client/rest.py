import httpx
import json
import logging
from typing import Dict, Any

from api_gateway.ig_client.auth import IGAuthenticator
from api_gateway.ig_client.core.exceptions import (
    IGAPIError,
    IGAuthenticationError,
    IGAuthorizationError,
    IGValidationError,
    IGRateLimitError,
    IGNotFoundError,
    IGServerError,
    IGNetworkError,
    IGTimeoutError,
)

logger = logging.getLogger(__name__)


class IGRest:
    def __init__(self, base_url: str, auth_session: IGAuthenticator):
        self.auth_session = auth_session
        self.client = httpx.Client(
            base_url=base_url,
            headers=auth_session.get_headers(),
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )

    def get(self, endpoint: str, version: str, **kwargs):
        return self._request(method="GET", endpoint=endpoint, version=version, **kwargs)

    def post(self, endpoint: str, version: str, data=None, **kwargs):
        return self._request(
            method="POST", endpoint=endpoint, version=version, json=data, **kwargs
        )

    def put(self, endpoint: str, version: str, data=None, **kwargs):
        return self._request(
            method="PUT", endpoint=endpoint, version=version, json=data, **kwargs
        )

    def delete(self, endpoint: str, version: str, data=None, **kwargs):
        return self._request(
            method="DELETE", endpoint=endpoint, version=version, json=data, **kwargs
        )

    def _request(self, method: str, endpoint: str, version: str, **kwargs):
        override_method = kwargs.pop("override_method", "")  # Remove from kwargs
        headers = self.auth_session.get_headers()
        headers["VERSION"] = version
        if override_method:
            headers["_method"] = override_method

        logger.debug(
            "Making API request",
            method=method,
            endpoint=endpoint,
            version=version,
            headers=headers,
        )

        try:
            response = self.client.request(
                method=method, url=endpoint, headers=headers, **kwargs
            )
            return self._handle_response(response)

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout for {method} {endpoint}: {str(e)}")
            raise IGTimeoutError(f"Request timeout: {str(e)}")

        except httpx.NetworkError as e:
            logger.error(f"Network error for {method} {endpoint}: {str(e)}")
            raise IGNetworkError(f"Network error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error in request {method} {endpoint}: {str(e)}")
            raise IGAPIError(f"Unexpected error: {str(e)}")

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        request_id = response.headers.get("X-Request-ID", "unknown")

        logger.debug(
            "API Response received",
            status_code=response.status_code,
            request_id=request_id,
            response_time=response.elapsed.total_seconds(),
            content_length=len(response.content) if response.content else 0,
        )

        if response.status_code == 200:
            return self._parse_json_response(response)

        elif response.status_code == 401:
            error_details = self._extract_error_details(response)
            raise IGAuthenticationError(
                message="Authentication failed or session expired",
                status_code=401,
                request_id=request_id,
                details=error_details,
            )

        elif response.status_code == 403:
            error_details = self._extract_error_details(response)
            raise IGAuthorizationError(
                message="Insufficient permissions for this operation",
                status_code=403,
                request_id=request_id,
                details=error_details,
            )

        elif response.status_code == 400:
            error_details = self._extract_error_details(response)
            error_code = error_details.get("errorCode", "Unknown validation error")
            raise IGValidationError(
                message=f"Request validation failed: {error_code}",
                status_code=400,
                error_code=error_code,
                request_id=request_id,
                details=error_details,
            )

        elif response.status_code == 404:
            error_details = self._extract_error_details(response)
            raise IGNotFoundError(
                message="Requested resource not found",
                status_code=404,
                request_id=request_id,
                details=error_details,
            )

        elif response.status_code == 429:
            error_details = self._extract_error_details(response)
            raise IGRateLimitError(
                message="Rate limit exceeded. Please retry after the specified time.",
                status_code=429,
                request_id=request_id,
                details=error_details,
            )

        elif 500 <= response.status_code < 600:
            error_details = self._extract_error_details(response)
            raise IGServerError(
                message=f"Server error: {response.text}",
                status_code=response.status_code,
                request_id=request_id,
                details=error_details,
            )

        else:
            error_details = self._extract_error_details(response)
            raise IGAPIError(
                message=f"Unexpected HTTP status: {response.status_code}",
                status_code=response.status_code,
                request_id=request_id,
                details=error_details,
            )

    def _extract_error_details(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            return response.json()
        except (ValueError, json.JSONDecodeError):
            return {
                "raw_response": response.text,
                "content_type": response.headers.get("content-type", "unknown"),
            }

    def _parse_json_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            return response.json()
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse JSON response: {str(e)}")
            return {"raw_response": response.text}
