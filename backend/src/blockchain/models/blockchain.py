# encoding: utf-8

import re
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from pydantic import ValidationError

from src.blockchain.models.block import Block
from src.blockchain.schemas.blockchain import BlockchainSchema
from src.config.settings import MINING_REWARD_INPUT
from src.exceptions import BlockchainError, TransactionError

# Custom logger for blockchain class module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class Blockchain(object):
    """
    Distributed inmutable ledger of blocks.
    """

    def __init__(self, chain: list = None):
        """
        Create a new Blockchain instance.

        :param list chain: chain of blocks.
        """
        self.chain = chain or [Block.genesis()]

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
        Get the blockchain chain length.

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
        :return Blockchain: validated blockchain.
        :raise BlockchainError: on chain validation error.
        """
        cls.is_valid_schema(chain)
        return cls(chain)

    @staticmethod
    def is_valid_schema(chain: list):
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
        to be validated for the rest of the nodes.

        :param data list: transactions data to be added to the next block.
        :return Block: new mined block.
        """
        block = Block.mine_block(self.last_block, data)
        self.chain.append(block)
        return block

    def set_valid_chain(self, chain: list):
        """
        Set locally the valid chain among the network nodes.
        The valid chain is the longest one between all the properly formatted chains.

        :param chain list: candidate chain to become the valid one.
        """
        try:
            assert len(chain) > self.length
            self.is_valid(chain)
        except (AssertionError, BlockchainError) as err:
            len_error = 'Incoming chain is not longer than local chain.'
            message = err.message if hasattr(err, 'message') else len_error
            logger.error(f'[Blockchain] Replace error. {message}')
        else:
            self.chain = chain
            message = f'Blockchain length: {self.length}. Last block: {self.last_block}.'
            logger.info(f'[Blockchain] Replace successfull. {message}')

    @classmethod
    def is_valid(cls, chain: list):
        """
        Perform checks to candidate blockchain. If the chain is validated
        will become the new distributed chain over the network for all the
        nodes by consensus.

        :param list chain: candidate chain to become the distributed chain.
        :raise BlockchainError: on chain validation error.
        """
        cls.is_valid_schema(chain)
        cls.is_valid_transaction_data(chain)

    @staticmethod
    def is_valid_transaction_data(chain: list):
        """
        Perform checks to enforce the consistnecy of transactions data in the chain blocks:
        Each transaction mush only appear once in the chain, there can only be one mining
        reward per block and each transaction must be valid.

        :param list chain: blockchain chain of blocks.
        :raise BlockchainError: on invalid transaction data.
        """
        from src.client.models.transaction import Transaction
        from src.client.models.wallet import Wallet
        transaction_uuids = set()
        for index, block in enumerate(chain, start=0):
            has_reward = False
            for transaction_info in block.data:
                try:
                    transaction = Transaction.create(**transaction_info)
                    Transaction.is_valid(transaction)
                except TransactionError as err:
                    message = f'Invalid transaction. {err.message}.'
                    logger.error(f'[Blockchain] Validation error. {message}')
                    raise BlockchainError(message)

                if transaction.uuid in transaction_uuids:
                    message = f'Repetead transaction uuid found: {transaction.uuid}.'
                    logger.error(f'[Blockchain] Validation error. {message}')
                    raise BlockchainError(message)
                transaction_uuids.add(transaction.uuid)

                address = transaction.input.get('address')
                if address == MINING_REWARD_INPUT.get('address'):
                    if has_reward:
                        message = f'Multiple mining rewards in the same block: {block}.'
                        logger.error(f'[Blockchain] Validation error. {message}')
                        raise BlockchainError(message)
                    has_reward = True
                else:
                    historic_blockchain = Blockchain()
                    historic_blockchain.chain = chain[:index]
                    historic_balance = Wallet.get_balance(historic_blockchain, address)
                    amount = transaction.input.get('amount')
                    if historic_balance != amount:
                        message = f'Address {address} historic balance inconsistency: {historic_balance} ({amount}).'
                        logger.error(f'[Blockchain] Validation error. {message}')
                        raise BlockchainError(message)
