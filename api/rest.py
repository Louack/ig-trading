from typing import Dict

import httpx

from api.auth import IGAuthenticator
from core.exceptions import IGAuthenticationError


class IGRest:
    def __init__(self, base_url: str, auth_session: IGAuthenticator):
        self.auth_session = auth_session
        self.client = httpx.Client(
            base_url=base_url, headers=auth_session.get_headers()
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

    def delete(self, endpoint: str, version: str, **kwargs):
        return self._request(
            method="DELETE", endpoint=endpoint, version=version, **kwargs
        )

    def _request(self, method: str, endpoint: str, version: str, **kwargs):
        headers = self.auth_session.get_headers()
        headers["VERSION"] = version
        response = self.client.request(
            method=method, url=endpoint, headers=headers, **kwargs
        )
        return self._handle_response(response)

    @staticmethod
    def _handle_response(response: httpx.Response):
        if response.status_code == 401:
            raise IGAuthenticationError("Authentication failed or session expired")
        if response.status_code == 429:
            raise IGAuthenticationError("Rate limit exceeded")
        if response.status_code >= 400:
            raise IGAuthenticationError(f"HTTP {response.status_code}: {response.text}")

        try:
            return response.json()
        except ValueError:
            return response.text
