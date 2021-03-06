import requests
import time 
from backend.wallet.wallet import Wallet
"""
This testing script automates the transaction-mine cycle. 
"""

BASE_URL = "http://localhost:5000"

def get_blockchain():
    return requests.get(f"{BASE_URL}/blockchain").json()

def get_blockchain_mine():
    return requests.get(f"{BASE_URL}/blockchain/mine").json()

def post_wallet_transact(recipient, amt):
    return requests.post(
        f"{BASE_URL}/wallet/transact",
        json={ "recipient": recipient, "amount": amt }
    ).json()

def get_wallet_info():
    return requests.get(f"{BASE_URL}/wallet/info").json()

init = get_blockchain()
print(f"Blockchain:  {init}")

recipient = Wallet().address
# Broadcast Tx 1
tx_1 = post_wallet_transact(recipient, 13)
input_1 = tx_1["input"]

print(f"""
Transaction I (ID: {tx_1["id"]})
==========================================
Transaction I Input:
address: {input_1["address"]}
amount: {input_1["amount"]}
public_key: {input_1["public_key"]}
signature: {input_1["signature"]}
timestamp: {input_1["timestamp"]}
==========================================
Transaction I Output: {tx_1["output"]}  
==========================================\n
""")
# Broadcast Tx 2
time.sleep(1)
tx_2 = post_wallet_transact(recipient, 39)
# for i in tx_2:
#     print(f"\nTransaction II: {i}, {tx_2[i]}")
# list(map(lambda i: out_2[i], out_2))
input_2 = tx_2["input"]
out_2 = tx_2["output"]

print(f"""
Transaction II (ID: {tx_2["id"]})
==========================================
Transaction II Input:
address: {input_2["address"]}
amount: {input_2["amount"]}
public_key: {input_2["public_key"]}
signature: {input_2["signature"]}
timestamp: {input_2["timestamp"]}
==========================================
Transaction II Output: {tx_2["output"]}  
==========================================\n
""")
# Mine Block w/preceding Txs
time.sleep(1) # sleep to allow broadcast to Tx Pool
mined_block = get_blockchain_mine()
mined_data = mined_block["data"][0]
print(f"""
Mined Block I (ID: {mined_data["id"]})
==========================================
Mined Block I Input: 
address: {mined_data["input"]["address"]}
amount: {mined_data["input"]["amount"]}
public_key: {mined_data["input"]["public_key"]}
signature: {mined_data["input"]["signature"]}
timestamp: {mined_data["input"]["timestamp"]}
==========================================
Mined Block I Output: {mined_data["output"]}
==========================================\n
BLOCK INPUT RAW: {mined_block}
""")

wallet_info = get_wallet_info()
print(f"""
Wallet Information: 
==========================================
Address: {wallet_info["Address"]}
Balance: {wallet_info["Balance"]}
==========================================
""")