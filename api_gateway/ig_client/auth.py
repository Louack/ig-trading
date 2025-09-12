import httpx

from api_gateway.ig_client.core.exceptions import IGAuthenticationError


class IGAuthenticator:
    def __init__(self, base_url: str, api_key: str, identifier: str, password: str):
        self.base_url = base_url
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.tokens = {}

    def login(self):
        body = {
            "identifier": self.identifier,
            "password": self.password,
        }

        headers = {
            "X-IG-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        with httpx.Client(base_url=self.base_url, headers=headers) as client:
            response = client.post("/session", json=body)

        if response.status_code != 200:
            raise IGAuthenticationError(response.text)

        self.tokens = {
            "X-IG-API-KEY": self.api_key,
            "CST": response.headers.get("CST"),
            "X-SECURITY-TOKEN": response.headers.get("X-SECURITY-TOKEN"),
        }

        return self.tokens

    def get_headers(self):
        if not self.tokens:
            return self.login()
        return self.tokens
