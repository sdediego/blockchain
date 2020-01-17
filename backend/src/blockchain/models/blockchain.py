# encoding: utf-8

import re
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from pydantic import ValidationError

from src.blockchain.models.block import Block
from src.blockchain.schemas.blockchain import BlockchainSchema
from src.exceptions import BlockchainError

# Custom logger for blockchain class module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class Blockchain(object):
    """
    Distributed inmutable ledger of blocks.
    """
    
    def __init__(self, chain: list):
        """
        Create a new Blockchain instance.

        :param list chain: chain of blocks.
        """
        self.chain = chain
    
    def __str__(self):
        """
        Represent class instance via params string.

        :return str: instance representation.
        """
        return f'Blockchain: [{", ".join([str(block) for block in self.chain])}]'
    
    @property
    def genesis(self):
        """
        Get the first block of the blockchain called genesis block.

        :return Block: first block of the blockchain.
        """
        return self.chain[0]

    @property
    def last_block(self):
        """
        Get the last block of the blockchain.

        :return Block: last block of the blockchain.
        """
        return self.chain[-1]
    
    @property
    def length(self):
        """
        Get the blockchain length.

        :return int: blockchain length.
        """
        return len(self.chain)

    def serialize(self):
        """
        Stringify the blocks in the chain.

        :return list: chain of stringified blocks.
        """
        return list(map(lambda block: block.serialize(), self.chain))
    
    @classmethod
    def deserialize(cls, chain: list):
        """
        Create a new Blockchain instance from the provided serialized chain.

        :param list chain: serialized chain of blocks.
        :return Blockchain: blockchain created from provided stringified chain.
        """
        chain = list(map(lambda block: Block.deserialize(block), chain))
        return cls(chain)

    @classmethod
    def create(cls, chain: list):
        """
        Initialize a new instance after performing attributes validations
        and checking blockchain data integrity.

        :param list chain: chain of blocks.
        :return Blockchain: validated blockchain instance.
        """
        cls._is_valid_schema(chain)
        return cls(chain)

    @staticmethod
    def _is_valid_schema(chain: list):
        """
        Perform blockchain attribute validation and check data integrity.

        :param list chain: chain of blocks.
        :raise BlockchainError: on chain validation error.
        """
        try:
            BlockchainSchema(chain=chain)
        except ValidationError as err:
            message = re.sub('\s+',' ', err.json())
            logger.error(f'[Blockchain] Validation error. {message}')
            raise BlockchainError(message)

    def add_block(self, data: list):
        """
        Mine new block and add it to the local blockchain. If new block
        is mined the candidate blockchain will be send over the network
        to be validated for the rest of the peers.

        :param data list: transactions data to be added to the next block.
        """
        block = Block.mine_block(self.last_block, data)
        self.chain.append(block)
    
    @classmethod
    def is_valid(cls, chain: list):
        """
        Perform checks to candidate blockchain. If the chain is validated
        will become the new distributed chain over the network for all the
        nodes by consensus.

        :param list chain: candidate chain to become the distributed chain.
        """
        cls._is_valid_schema(chain)