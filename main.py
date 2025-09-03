from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
import httpx


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

    def login(self) -> bool:
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

    def get_accounts(self):
        resp = self.client.get("/accounts")
        resp.raise_for_status()

        return resp.json()


if __name__ == "__main__":
    client = IGClient(account_type="demo")
    client.login()
    print(client.get_accounts())
