# encoding: utf-8

# Block settings
BLOCK_HASH_LENGTH = 64
BLOCK_MINING_RATE = 30 * 1000  # milliseconds (30 secs)
BLOCK_TIMESTAMP_LENGTH = 13    # milliseconds

GENESIS_BLOCK = {
    'index': 1,
    'timestamp': 1,
    'nonce': 0,
    'difficulty': 1,
    'data': [],
    'last_hash': 'genesis_last_hash',
    'hash': 'genesis_hash'
}
