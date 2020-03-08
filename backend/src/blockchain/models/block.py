# encoding: utf-8

import json
import re
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from pydantic import ValidationError

from src.blockchain.models import utils
from src.blockchain.schemas.block import BlockSchema
from src.config.settings import BLOCK_MINING_RATE, GENESIS_BLOCK
from src.exceptions import BlockError

# Custom logger for block class module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class Block(object):
    """
    Storage unit of transactions between the nodes of the network.
    The blocks are linked sequencially creating an inmutable distributed
    ledger called blockchain.
    """

    def __init__(self, index: int, timestamp: int, nonce: int,
                 difficulty: int, data: list, last_hash: str, hash: str):
        """
        Create a new Block instance.

        :param int index: block number in the blockchain.
        :param int timestamp: block creation UTC epoch datetime in milliseconds.
        :param int nonce: arbitrary number for cryptographic security.
        :param int difficulty: block mining difficulty according to mining rate.
        :param list data: transactions between the nodes in the network.
        :param str last_hash: previous block hash to link the blockchain.
        :param str hash: block data unique hash to prevent fraud.
        """
        self.index = index
        self.timestamp = timestamp
        self.nonce = nonce
        self.difficulty = difficulty
        self.data = data
        self.last_hash = last_hash
        self.hash = hash

    def __str__(self):
        """
        Represent class instance via params string.

        :return str: instance representation.
        """
        return ('Block('
            f'index: {self.index}, '
            f'timestamp: {self.timestamp}, '
            f'nonce: {self.nonce}, '
            f'difficulty: {self.difficulty}, '
            f'data: {self.data}, '
            f'last_hash: {self.last_hash}, '
            f'hash: {self.hash})')

    def __eq__(self, block: 'Block'):
        """
        Compare two Block instances to check wether if both are the same
        block or not based on their unique hashes.

        :param Block block: other block instance to compare with.
        :return bool: true/false on block comparison.
        """
        return self.hash == block.hash

    @property
    def info(self):
        """
        Get block attributes in dict format.

        :return dict: dictionary of key-value block attributes.
        """
        return self.__dict__

    def serialize(self):
        """
        Stringify the Block instance to be able to send the block over
        the network to the rest of the peer nodes.

        :return str: block instance attributes in string format.
        :raise BlockError: on data encoding error.
        """
        try:
            return json.dumps(self.info)
        except (OverflowError, TypeError) as err:
            message = f'Could not encode block data. {err.args[0]}.'
            logger.error(f'[Block] Serialization error. {message}')
            raise BlockError(message)

    @classmethod
    def deserialize(cls, block_info: str):
        """
        Create a new Block instance from the provided stringified block.

        :param str block_info: stringified block.
        :return Block: block instance created from provided attributes.
        :raise BlockError: on data decoding error.
        """
        try:
            block_info = json.loads(block_info)
        except (OverflowError, TypeError) as err:
            message = f'Could not decode provided block json data. {err.args[0]}.'
            logger.error(f'[Block] Deserialization error. {message}')
            raise BlockError(message)
        return cls(**block_info)

    @classmethod
    def create(cls, index: int, timestamp: int, nonce: int,
               difficulty: int, data: list, last_hash: str, hash: str):
        """
        Initialize a new class instance after performing attributes validations
        and checking block data integrity.

        :param int index: block number in the blockchain.
        :param int timestamp: block creation UTC epoch datetime in milliseconds.
        :param int nonce: arbitrary number for cryptographic security.
        :param int difficulty: block mining difficulty according to mining rate.
        :param list data: transactions between the nodes in the network.
        :param str last_hash: previous block hash to link the blockchain.
        :param str hash: block data unique hash to prevent fraud.
        :return Block: new class instance.
        :raise BlockError: on attributes validation error.
        """
        kwargs = locals().copy()
        kwargs.pop('cls')
        block_info = {key: value for key, value in kwargs.items()}
        cls.is_valid_schema(block_info)
        return cls(**block_info)

    @staticmethod
    def is_valid_schema(block_info: dict):
        """
        Perform block attributes validations and check block data integrity.

        :param dict block_info: block attributes.
        :raise BlockError: on attributes validation error.
        """
        try:
            BlockSchema(**block_info)
        except ValidationError as err:
            message = re.sub('\s+',' ', err.json())
            logger.error(f'[Block] Validation error. {message}')
            raise BlockError(message)

    @classmethod
    def genesis(cls):
        """
        Create the first block for the blockchain called the genesis block.

        :return Block: first block (genesis) in the blockchain.
        """
        return cls(**GENESIS_BLOCK)

    @classmethod
    def mine_block(cls, last_block: 'Block', data: list):
        """
        Create a new Block instance to add to the blockchain.

        :param Block last_block: current last block of the blockchain.
        :param list data: transactions between the nodes in the network.
        :return Block: new block instance.
        """
        block = {}
        block['index'] = last_block.index + 1
        block['timestamp'] = utils.get_utcnow_timestamp()
        block['nonce'] = 0
        block['difficulty'] = cls.adjust_difficulty(last_block, block['timestamp'])
        block['data'] = data
        block['last_hash'] = last_block.hash
        block = cls.proof_of_work(last_block, block)
        return cls.create(**block)

    @classmethod
    def proof_of_work(cls, last_block: 'Block', block: dict):
        """
        Consensus protocol requiring certain computational effort to mine
        a new block to be able to add it to the blockchain. The solution
        is then verified by the entire network.

        :param Block last_block: current last block of the blockchain.
        :param dict block: block attributes except the unknown block hash.
        :return dict: block data for the next block in the blockchain.
        """
        block_values = block.values()
        hash = utils.hash_block(*block_values)
        while not utils.hex_to_binary(hash).startswith('0' * block['difficulty']):
            block['nonce'] += 1
            block['timestamp'] = utils.get_utcnow_timestamp()
            block['difficulty'] = cls.adjust_difficulty(last_block, block['timestamp'])
            hash = utils.hash_block(*block_values)
        block['hash'] = hash
        return block

    @staticmethod
    def adjust_difficulty(last_block: 'Block', timestamp: int):
        """
        Adjust new block mining difficulty to maintain stable mining rate.

        :param Block last_block: current last block in the blockchain.
        :param int timestamp: new block creation UTC epoch datetime in milliseconds.
        :return int: adjusted block difficulty.
        """
        if last_block.timestamp + BLOCK_MINING_RATE > timestamp:
            return last_block.difficulty + 1
        return last_block.difficulty - 1 if last_block.difficulty > 1 else 1

    @classmethod
    def is_valid(cls, last_block: 'Block', block: 'Block'):
        """
        Perform checks to candidate block before adding it to the blockchain
        to prevent fraudulent insertions into the blockchain. Block attributes
        must fullfill certain conditions for the block to be valid.

        :param Block last_block: current last block in the blockchain.
        :param Block block: candidate block to add to the blockchain.
        :raise BlockError: on invalid block attributes.
        """
        cls.is_valid_schema(block.info)

        messages = []
        if block.last_hash != last_block.hash:
            message = (f'Block {last_block.index} hash "{last_block.hash}" and '
                       f'block {block.index} last_hash "{block.last_hash}" must match.')
            messages.append(message)
        if abs(last_block.difficulty - block.difficulty) > 1:
            message = (f'Difficulty must differ as much by 1 between blocks: '
                       f'block {last_block.index} difficulty: {last_block.difficulty}, '
                       f'block {block.index} difficulty: {block.difficulty}.')
            messages.append(message)

        if messages:
            for message in messages:
                logger.error(f'[Block] Validation error. {message}')
            raise BlockError("\n".join(messages))
