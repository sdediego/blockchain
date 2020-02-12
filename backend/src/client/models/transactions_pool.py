# encoding: utf-8

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from src.blockchain.models.blockchain import Blockchain
from src.client.models.transaction import Transaction

# Custom logger for transaction pool class module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class TransactionsPool(object):
    """
    Collection of unconfimed transactions.
    A set of transactions from the pool will be mined and added to the blockchain
    in each future block to confirm the transactions.
    """

    def __init__(self, pool: dict = None):
        """
        Create a new transactions pool instance.
        """
        self.pool = pool or {}

    def __str__(self):
        """
        Represent class instance via params string.

        :return str: instance representation.
        """
        return f'Transactions pool: [{", ".join([str(transaction) for transaction in self.pool.values()])}]'

    @property
    def size(self):
        """
        Get the transactions pool size.

        :return int: number of unconfirmed transactions in the pool.
        """
        return len(self.pool)

    def serialize(self):
        """
        Stringify the transactions in the pool.

        :return list: list of stringified transactions.
        """
        return list(map(lambda transaction: transaction.serialize(), self.pool.values()))

    @classmethod
    def deserialize(cls, pool: list):
        """
        Create a new transactions pool instance from the provided serialized pool.

        :param list pool: serialized pool of transactions.
        :return TransactionsPool: transactions pool created from provided stringified pool.
        """
        transactions = list(map(lambda transaction: Transaction.deserialize(transaction), pool))
        pool = {transaction.uuid: transaction for transaction in transactions}
        return cls(pool)

    def get_transaction(self, address: str):
        """
        Get a transaction from the pool.

        :param str address: sender wallet address.
        :return Transaction: found transaction if exists.
        """
        for transaction in self.pool.values():
            if transaction.input.get('address') == address:
                message = f'Transaction found in the pool with sender address: {address}.'
                logger.info(f'[TransactionsPool] Get transaction. {message}')
                return transaction
        message = f'Transaction not found in the pool with sender address: {address}.'
        logger.warning(f'[TransactionsPool] Get transaction. {message}')
        return None

    def add_transaction(self, transaction: Transaction):
        """
        Insert a new transaction to the pool of unconfirmed transactions.

        :param Transaction transaction: transaction to add to the pool.
        """
        self.pool[transaction.uuid] = transaction
        message = f'New transaction added to the pool: {transaction}.'
        logger.info(f'[TransactionsPool] Add transaction. {message}')

    def clear_pool(self, blockchain: Blockchain):
        """
        Remove added transactions to the blockchain from the pool.

        :param Blockchain blockchain: network shared blockchain.
        """
        for block in blockchain.chain:
            for transaction in block.data:
                if transaction.uuid in self.pool.keys():
                    self.pool.pop(transaction.uuid)
                    message = f'Transaction cleared from pool: {transaction}.'
                    logger.info(f'[TransactionsPool] Clear transaction. {message}')
