# encoding: utf-8

from src.blockchain.models.utils import hash_block

# Block
BLOCK_HASH_LENGTH = 64
BLOCK_MINING_RATE = 10 * 1000  # milliseconds (10 secs)
BLOCK_TIMESTAMP_LENGTH = 13

GENESIS_BLOCK = {
    'index': 0,
    'timestamp': 1,
    'nonce': 0,
    'difficulty': 1,
    'data': [],
    'last_hash': 'genesis_last_hash'
}
GENESIS_BLOCK['hash'] = hash_block(*GENESIS_BLOCK.values())

# P2P Server
HEARTBEAT_RATE = 5  # seconds

NODE = 'node'
CHAIN = 'chain'
SYNCHRONIZE = 'sync'
TRANSACTION = 'transaction'
CHANNELS = {
    NODE: 'node',
    CHAIN: 'chain',
    SYNCHRONIZE: 'sync',
    TRANSACTION: 'transaction'
}

# Transaction
MINING_REWARD = 50
MINING_REWARD_INPUT = {'address': '*--mining-reward--*'}
