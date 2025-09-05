from functools import wraps
from tenacity import retry, stop_after_attempt, wait_fixed

from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
import httpx


def auto_relog(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                self.login()
                return func(self, *args, **kwargs)
            raise
    return wrapper


class IGClient:
    def __init__(self, account_type: str = "demo"):
        self.account_type = account_type
        self.api_key = API_KEYS[account_type]
        self.base_url = BASE_URLS[account_type]
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={"X-IG-API-KEY": self.api_key},
        )
        self.cst = None
        self.x_security_token = None

    def login(self):
        endpoint = "/session"
        body = {
            "identifier": IDENTIFIERS[self.account_type],
            "password": PASSWORDS[self.account_type],
        }

        headers = {
            "X-IG-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            resp = self.client.post(endpoint, json=body, headers=headers)
            resp.raise_for_status()

            self.cst = resp.headers.get("CST")
            self.x_security_token = resp.headers.get("X-SECURITY-TOKEN")

            self.client.headers.update(
                {
                    "CST": self.cst,
                    "X-SECURITY-TOKEN": self.x_security_token,
                }
            )
            print("Successful login")
        except httpx.HTTPStatusError:
            print("Failed login")

    @auto_relog
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def get_accounts(self):
        resp = self.client.get("/accounts", headers={"Version": "1"})
        resp.raise_for_status()
        return resp.json()
