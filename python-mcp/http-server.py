from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import httpx

mcp = FastMCP("Bank Server",
    host="localhost",
    port=8888
)

BASE_URL = "https://cymbal-bank.fsi.cymbal.dev"
session = requests.Session()

@mcp.tool()
def login(username: str, password: str) -> str:
    resp = session.post(
        f"{BASE_URL}/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if resp.status_code in (200, 303):
        return "Login successful"
    return f"Login failed: {resp.status_code} {resp.text[:200]}"

@mcp.tool()
def get_balance() -> str:
    resp = session.get(BASE_URL + "/")
    if resp.status_code != 200:
        return f"Error: {resp.status_code}"

    soup = BeautifulSoup(resp.text, "html.parser")
    balance_span = soup.find("span", {"id": "current-balance"})
    if balance_span:
        return f"Balance: {balance_span.get_text(strip=True)}"
    return "Balance not found in page."

@mcp.tool()
def send_payment(account_num: str, contact_account_num: str, contact_label: str, amount: str, uuid: str) -> str:
    resp = session.post(
        BASE_URL + "/payment",
        data={
            "account_num": account_num,
            "contact_account_num": contact_account_num,
            "contact_label": contact_label,
            "amount": amount,
            "uuid": uuid,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if resp.status_code in (200, 303):
        return f"Payment success: {resp.text[:200]}"
    return f"Payment failed: {resp.status_code} {resp.text[:200]}"

if __name__ == "__main__":
    # instead of mcp.run() over stdio:
    print('running sse')
    mcp.run(transport='sse')

