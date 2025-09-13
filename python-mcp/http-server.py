from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import httpx

mcp = FastMCP("Bank Server",
    host="0.0.0.0",
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
def send_payment(
    account_num: str,
    amount: str,
    uuid: str,
    contact_account_num: str = None,
    contact_label: str = None,
) -> str:
    """Send a payment to an account.

    Required:
    - account_num: The recipient account number.
    - amount: The amount to send.
    - uuid: any random uuid of format 'fe850d76-1a42-4129-b0b7-be0b23a90995 , this should be randomly generated newly everytime as duplicate transactions may fail the payment  'fe850d76-1a42-4129-b0b7-be0b23a90995'

    Optional:
    - contact_account_num: The account number to debit from.
    - contact_label: Label or name of the recipient.
    """

    # Build payload dynamically
    payload = {
        "account_num": account_num,
        "amount": amount,
        "uuid": uuid
    } 
    if contact_account_num:
        payload["contact_account_num"] = contact_account_num
    if contact_label:
        payload["contact_label"] = contact_label

    resp = session.post(
        BASE_URL + "/payment",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if resp.status_code in (200, 303):
        return f"Payment success: {resp.text[:6000]}"
    return f"Payment failed: {resp.status_code} {resp.text[:6000]}"

if __name__ == "__main__":
    # instead of mcp.run() over stdio:
    print('running sse')
    mcp.run(transport='sse')

