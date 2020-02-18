# encoding: utf-8

import uuid
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from pydantic import BaseModel, root_validator, validator
from pydantic.fields import Field

from src.client.models.wallet import Wallet
from src.config.settings import MINING_REWARD_INPUT

# Custom logger for transaction schema module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class TransactionSchema(BaseModel):
    """
    Schema for definition and validation of transaction attributes.
    """
    uuid: int = None
    input: dict = None
    output: dict = None
    sender: Wallet = None
    recipient: str = None
    amount: float = None

    class Config:
        title = 'Transaction schema'
        anystr_strip_whitespace = True
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def check_raw_input_data(cls, values: dict):
        """
        Check input raw data is s complete set of valid values.

        :param dict values: provided input raw values.
        :return dict: checked input raw values.
        :raise ValueError: if provided values set is incomplete.
        """
        if all([key in values.keys() for key in ('uuid', 'output', 'input')]):
            return values
        if all([key in values.keys() for key in ('sender', 'recipient', 'amount')]):
            return values
        message = f'Invalid set of transaction attributes: {values.keys()}.'
        logger.error(f'[TransactionSchema] Validation error. {message}')
        raise ValueError(message)

    @validator('uuid')
    def valid_uuid(cls, value: int):
        """
        Validate transaction unique identifier is correct integer.

        :param int value: provided unique identifier value.
        :return int: validated unique identifier value.
        :raise ValueError: if identifier is badly formed integer.
        """
        try:
            uuid.UUID(int=value)
        except ValueError as err:
            message = f'Invalid unique identifier integer value: {err.args[0]}.'
            logger.error(f'[TransactionSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('input')
    def valid_input(cls, value: dict):
        """
        Validate transaction input attributes are correct.

        :param dict value: provided transaction input value.
        :return dict: validated transaction input value.
        :raise ValueError: if input attributes are invalid.
        """
        keys = ('timestamp', 'amount', 'address', 'public_key', 'signature')
        try:
            if 'address' in value:
                if value.get('address') != MINING_REWARD_INPUT.get('address'):
                    assert all([key in value.keys() for key in keys])
            else:
                raise AssertionError
        except AssertionError:
            message = f'Invalid input: {value.keys()}.'
            logger.error(f'[TransactionSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('output')
    def valid_output(cls, value: dict, values: dict):
        """
        Validate transaction output attributes are correct.

        :param dict value: provided transaction output value.
        :return dict: validated transaction output value.
        :raise ValueError: if output attributes are invalid.
        """
        input = values.get('input')
        try:
            if 'address' in input:
                if input.get('address') != MINING_REWARD_INPUT.get('address'):
                    assert all([uuid.UUID(hex=key) for key in value.keys()])
                    assert all([isinstance(amount, float) for amount in value.values()])
            else:
                raise AssertionError
        except AssertionError:
            message = f'Invalid output: {value}.'
            logger.error(f'[TransactionSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('sender')
    def valid_sender_wallet(cls, value: Wallet):
        """
        Validate sender wallet balance is positive.

        :param Wallet value: provided sender wallet instance.
        :return Wallet: validated sender wallet instance.
        :raise ValueError: if wallet balance value is non-positive.
        """
        try:
            assert value.balance > 0 if hasattr(value, 'balance') else False
        except AssertionError:
            message = f'Balance must be greater than zero to make a transaction.'
            logger.error(f'[TransactionSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('recipient')
    def valid_recipient_address(cls, value: str):
        """
        Validate recipient address is correct hexadecimal string.

        :param str value: provided recipient address value.
        :return str: validated recipient address value.
        :raise ValueError: if address is badly formed hexadecimal string.
        """
        try:
            uuid.UUID(hex=value)
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
