import time
import backend.env_config as config
from pubnub.pubnub import PubNub
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNReconnectionPolicy
from backend.blockchain.block import Block
from backend.wallet.transaction import Transaction
 
pnconfig = PNConfiguration()
pnconfig.reconnect_policy = PNReconnectionPolicy.LINEAR
pnconfig.subscribe_key = config.pubsub["subscribe_key"]
pnconfig.publish_key = config.pubsub["publish_key"]

CHANNELS = {
    "TEST": "TEST",
    "BLOCK": "BLOCK",
    'TRANSACTION': 'TRANSACTION'
}

class Listener(SubscribeCallback):
    """
    Instantiates a listener, passing a unique blockchain instance.
    To evaluate broadcasted blocks, a copy of the local chain, or `prospective_chain`, is
    generated, to which the broadcast block is appended. This prospective instance is then
    evaluated for chain surrogation.
    """
    def __init__(self, blockchain, transaction_pool):
        self.blockchain = blockchain 
        self.transaction_pool = transaction_pool

    def message(self, pubnub, message_obj):
        print(f"\n -- Channel: {message_obj.channel} | Message: {message_obj.message}")

        if (message_obj.channel == CHANNELS["BLOCK"]):
            prospective_block = Block.deserialize_from_json(message_obj.message)
            prospective_chain = self.blockchain.chain[:]
            prospective_chain.append(prospective_block)

            try:
                self.blockchain.surrogate_chain(prospective_chain)
                # purge recorded Tx from Pool
                self.transaction_pool.purge(self.blockchain)
                print(f"\n -- Chain surrogation successful.")
            except Exception as err:
                print(f"\n -- Chain surrogation failed. See: {err}")

        elif (message_obj.channel == CHANNELS["TRANSACTION"]):
            transaction = Transaction.deserialize_from_json(message_obj.message)
            self.transaction_pool.set_transaction(transaction)
            print("\n -- New transaction successfully broadcast, added to the transaction pool.")

class PubSub():
    """
    Manages the publish/subscribe layer of the application, affording
    scalable communications infrastructure across nodes.
    """
    def __init__(self, blockchain, transaction_pool):
        self.pubnub = PubNub(pnconfig)
        self.pubnub.subscribe().channels(CHANNELS.values()).execute()
        self.pubnub.add_listener(Listener(blockchain, transaction_pool))

    def publish(self, channel_str, message_obj):
        """
        Publish given message obj to given channel.
        """
        self.pubnub.publish().channel(channel_str).message(message_obj).sync()

    def broadcast_block(self, block):
        """
        Broadcast a block obj to all nodes.
        """
        self.publish(CHANNELS["BLOCK"], block.serialize_to_json())

    def broadcast_transaction(self, transaction):
        """
        Broadcast a transaction obj to all nodes.
        """
        self.publish(CHANNELS['TRANSACTION'], transaction.serialize_to_json())

def main():
    pubsub = PubSub()

    time.sleep(1)
    pubsub.publish(CHANNELS["TEST"], { "foo": "bar" })

if __name__ == "__main__":
    main()
