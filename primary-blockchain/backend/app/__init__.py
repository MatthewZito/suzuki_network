import os
import random
import requests
from backend.config import FRONTEND_ADDRESS
from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.blockchain.blockchain import Blockchain
from backend.pubsub import PubSub
from backend.wallet.wallet import Wallet
from backend.wallet.transaction import Transaction
from backend.wallet.transaction_pool import TransactionPool

app = Flask(__name__)
CORS(app, resources={ r"/*": { "origins": f"{FRONTEND_ADDRESS}"} })  # add CORS Policy for all endpoints
blockchain = Blockchain()
wallet = Wallet(blockchain)
transaction_pool = TransactionPool()
pubsub = PubSub(blockchain, transaction_pool)

@app.route("/")
def default_route():
    return "Welcome"

@app.route("/blockchain")
def blockchain_route():
    return jsonify(blockchain.serialize_to_json())

@app.route("/blockchain/mine")
def mine_block_route():
    """
    Mine blocks on the shared chain. If given wallet is first to validate a given block, 
    `prospective_mining_reward` will be allocated into given wallet UTXO. Else, the reward 
    transaction will be void.
    """
    # serialize all Tx 
    tx_data = transaction_pool.serialize_to_json()
    # generate, serialize mining reward transaction obj
    prospective_mining_reward = Transaction.generate_reward_transaction(wallet).serialize_to_json()
    # append reward Tx and submit
    tx_data.append(prospective_mining_reward)
    blockchain.add_block(tx_data)
    block = blockchain.chain[-1]
    pubsub.broadcast_block(block)
    transaction_pool.purge(blockchain)
    
    return jsonify(block.serialize_to_json())

# @app.route("/wallet")
# def wallet_route():
#     return wallet.balance

@app.route("/wallet/transact", methods=["POST"])
def wallet_transaction_route():
    tx_data = request.get_json()
    transaction = transaction_pool.existing_transaction(wallet.address)
    
    if transaction:
        transaction.tx_update(
        wallet,
        tx_data["recipient"],
        tx_data["amount"]
    )
    else:
        transaction = Transaction(
            wallet,
            tx_data["recipient"],
            tx_data["amount"]
        )
    
    pubsub.broadcast_transaction(transaction)

    return jsonify(transaction.serialize_to_json())

@app.route("/wallet/info")
def wallet_info_route():
    return jsonify({"Address" : wallet.address, "Balance" : wallet.balance})

ROOT_PORT = 5000
PORT = ROOT_PORT

# peer instance, supports up to 1,000 peers
if os.environ.get("PEER") == "True":
    PORT = random.randint(5001, 6000)

    # fetch blockchain instance
    res = requests.get(f"http://localhost:{ROOT_PORT}/blockchain")
    res_blockchain = Blockchain.deserialize_from_json(res.json())
    try:
        blockchain.surrogate_chain(res_blockchain)
        print("\n -- Successfully synchronized local blockchain instance.")
    except Exception as err:
        print(f"\n -- Error synchronizing local blockchain instance. See: {err}")

app.run(port=PORT)