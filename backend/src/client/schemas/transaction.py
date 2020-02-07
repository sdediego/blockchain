# encoding: utf-8

import uuid
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from pydantic import BaseModel, validator
from pydantic.fields import Field

from src.client.models.wallet import Wallet

# Custom logger for transaction schema module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class TransactionSchema(BaseModel):
    """
    Schema for definition and validation of transaction attributes.
    """
    sender: Wallet
    recipient: str
    amount: float

    class Config:
        title = 'Transaction schema'
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True
        validate_all = True

    @validator('sender')
    def valid_sender_wallet(cls, value: Wallet):
        """
        Validate sender wallet balance is positive.

        :param Wallet value: provided sender wallet instance.
        :raise ValueError: if wallet balance value is non-positive.
        """
        try:
            assert value.balance > 0 if hasattr(value, 'balance') else False
        except AssertionError:
            message = f'Amount must be greater than zero to make transaction.'
            logger.error(f'[TransactionSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('recipient')
    def valid_recipient_address(cls, value: str):
        """
        Validate recipient address is correct hexadecimal string.

        :param str value: provided recipient address value.
        :raise ValueError: if address is badly formed hexadecimal string.
        """
        try:
            uuid.UUID(value)
        except ValueError as err:
            message = f'Invalid recipient address value: {err.args[0]}.'
            logger.error(f'[TransactionSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('amount')
    def valid_amount(cls, value: float, values: dict):
        """
        Validate exchange amount value.

        :param float value: provided amount value.
        :param dict values: previous fields already validated.
        :return float: validated amount value.
        :raise ValueError: if exchange amount is less than sender balance.
        """
        sender = values.get('sender', Wallet())
        try:
            assert sender.balance > value
        except AssertionError:
            message = f'Amount {value} exceeds wallet balance {sender.balance}.'
            logger.error(f'[TransactionSchema] Validation error. {message}')
            raise ValueError(message)
        return value
