# encoding: utf-8

import json
import re
import uuid
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join
from typing import Union

from pydantic import ValidationError

from src.client.models.utils import get_utcnow_timestamp
from src.client.models.wallet import Wallet
from src.client.schemas.transaction import TransactionSchema
from src.config.settings import MINING_REWARD, MINING_REWARD_INPUT
from src.exceptions import TransactionError

# Custom logger for transaction class module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class Transaction(object):
    """
    Collection of certain amount of cryptocurrency exchange between a unique
    sender wallet address and one or more recipients.
    """
    
    def __init__(self, uuid: int = None, output: dict = None, input: dict = None,
                 sender: Wallet = None, recipient: str = None, amount: float = None):
        """
        Create a new transaction instance.

        :param int uuid: unique identifier integer.
        :param dict output: transaction output information.
        :param dict input: transaction input information.
        :param Wallet sender: cryptocurrency sender wallet.
        :param str recipient: cryptocurrency recipient address.
        :param float amount: amount of cryptocurrency to exchange.
        """
        self.uuid = uuid or self.generate_uuid()
        self.output = output or self.generate_output(sender, recipient, amount)
        self.input = input or self.generate_input(sender)

    def __str__(self):
        """
        Represent class instance via params string.

        :return str: instance representation.
        """
        return ('Transaction('
            f'uuid: {self.uuid}, '
            f'input: {self.input}, '
            f'output: {self.output})')

    @staticmethod
    def generate_uuid():
        """
        Create a transaction unique identifier.

        :return int: unique identifier as a 128-bit integer.
        """
        return uuid.uuid4().int

    @staticmethod
    def generate_output(sender: Wallet, recipient: str, amount: float):
        """
        Create output data structure for the transaction.

        :param Wallet sender: cryptocurrency sender wallet.
        :param str recipient: cryptocurrency recipient address.
        :param float amount: amount of cryptocurrency to exchange.
        :return dict: transaction output data.
        """
        output = {}
        output[recipient] = amount
        output[sender.address] = sender.balance - amount
        return output

    def generate_input(self, sender: Wallet):
        """
        Create input data structure for the transaction.

        :param Wallet sender: cryptocurrency sender wallet.
        :param dict output: transaction output.
        :return dict: transaction input data.
        """
        input = {}
        input['timestamp'] = get_utcnow_timestamp()
        input['amount'] = sender.balance
        input['address'] = sender.address
        input['public_key'] = sender.public_key
        input['signature'] = sender.sign(self.output)
        return input

    @property
    def info(self):
        """
        Get transaction attributes in dict format.

        :return dict: dictionary of key-value transaction attributes.
        """
        return self.__dict__

    def serialize(self):
        """
        Stringify the transaction instance.

        :return str: transaction instance attributes in string format.
        :raise TransactionError: on encoding error.   
        """
        try:
            return json.dumps(self.info)
        except (OverflowError, TypeError) as err:
            message = f'Could not encode transaction data. {err.args[0]}.'
            logger.error(f'[Transaction] Serialization error. {message}')
            raise TransactionError(message)

    @classmethod
    def deserialize(cls, transaction_info: str):
        """
        Create a new transaction instance from the provided stringified transaction.

        :param str transaction_info: stringified transaction.
        :return Transaction: transaction instance created from provided attributes.
        :raise TransactionError: on decoding error.   
        """
        try:
            transaction_info = json.loads(transaction_info)
        except (OverflowError, TypeError) as err:
            message = f'Could not decode provided transaction json data. {err.args[0]}.'
            logger.error(f'[Transaction] Deserialization error. {message}')
            raise TransactionError(message)
        return cls(**transaction_info)

    @classmethod
    def create(cls, uuid: int = None, output: dict = None, input: dict = None,
               sender: Wallet = None, recipient: str = None, amount: float = None):
        """
        Initialize a new class instance after performing attributes validations
        and checking block data integrity.

        :param int uuid: unique identifier integer.
        :param dict output: transaction output information.
        :param dict input: transaction input information.
        :param Wallet sender: cryptocurrency sender wallet.
        :param str recipient: cryptocurrency recipient address.
        :param float amount: amount of cryptocurrency to exchange.
        :return Transaction: new transaction instance.
        """
        kwargs = locals().copy()
        kwargs.pop('cls')
        transaction_info = {key: value for key, value in kwargs.items() if value is not None}
        cls.is_valid_schema(transaction_info)
        return cls(**transaction_info)

    @staticmethod
    def is_valid_schema(transaction_info: dict):
        """
        Perform transaction attributes validations.

        :param dict transaction_info: transaction attributes.
        :raise TransactionError: on attributes validation error.
        """
        try:
            TransactionSchema(**transaction_info)
        except ValidationError as err:
            message = re.sub('\s+',' ', err.json())
            logger.error(f'[Transaction] Validation error. {message}')
            raise TransactionError(message)

    @staticmethod
    def is_valid(transaction: Union[dict, 'Transaction']):
        """
        Perform transaction logic validations.

        :param Transaction transaction: transaction instance to verify.
        :raise TransactionError: on transaction validation error.
        """
        transaction = transaction if not isinstance(transaction, dict) else Transaction(**transaction)
        Transaction.is_valid_schema(transaction.info)
        if transaction.input.get('address') != MINING_REWARD_INPUT.get('address'):
            amount = sum(transaction.output.values())
            if not transaction.input.get('amount') == amount:
                message = f'Invalid transaction amount: {amount}.'
                logger.error(f'[Transaction] Validation error. {message}')
                raise TransactionError(message)
            public_key = transaction.input.get('public_key')
            signature = transaction.input.get('signature')
            output = transaction.output
            if not Wallet.verify(public_key, signature, output):
                message = 'Invalid signature verification.'
                logger.error(f'[Transaction] Validation error. {message}')
                raise TransactionError(message)

    @staticmethod
    def reward_mining(wallet: Wallet):
        """
        Generate a reward transaction to award the miner when a new
        block is mined. The mining reward is a fix amount.

        :param Wallet wallet: miner wallet.
        :return Transaction: reward transaction.
        """
        output = {wallet.address: MINING_REWARD}
        input = MINING_REWARD_INPUT
        uuid = Transaction.generate_uuid()
        return Transaction.create(uuid=uuid, input=input, output=output)

    def update(self, sender: Wallet, recipient: str, amount: float):
        """
        Update existing transaction for a sender with an existing or
        a new recipient address.

        :param Wallet sender: cryptocurrency sender wallet.
        :param str recipient: cryptocurrency recipient address.
        :param float amount: amount of cryptocurrency to exchange.
        :raise TransactionError: on attributes validation error.
        """
        address = sender.address
        if amount > self.output.get(address):
            message = f'Amount {amount} exceeds sender available balance {self.output.get(address)}.'
            logger.error(f'[Transaction] Invalid amount. {message}')
            raise TransactionError(message)
        self.output[recipient] = self.output.get(recipient) + amount if recipient in self.output else amount
        self.output[address] = self.output.get(address) - amount
        self.input = self.generate_input(sender)
