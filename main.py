from client import IGClient
from settings import BASE_URLS, API_KEYS, IDENTIFIERS, PASSWORDS
import httpx


if __name__ == "__main__":
    client = IGClient(account_type="prod")
    client.login()
    client.get_accounts()
