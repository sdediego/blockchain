# encoding: utf-8

import math
import re
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from pydantic import BaseModel, ValidationError, validator
from pydantic.fields import Field

from src.blockchain.models.utils import hash_block, hex_to_binary
from src.config.settings import BLOCK_HASH_LENGTH, BLOCK_TIMESTAMP_LENGTH


# Custom logger for block schema module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class BlockSchema(BaseModel):
    """
    Schema for definition and validation of block attributes.
    """
    index: int
    timestamp: int
    nonce: int
    difficulty: int
    data: list
    last_hash: str
    hash: str

    class Config:
        title = 'Block schema'
        anystr_strip_whitespace = True
        validate_all = True

    @validator('index', 'nonce', 'difficulty')
    def valid_positive_integer(cls, value: int, field: Field):
        """
        Validate positive integer value.

        :param int value: provided integer value.
        :param Field field: field name to validate its value.
        :return int: validated integer value.
        :raise ValueError: if integer value is non-positive integer (or zero).
        """
        try:
            assert value > 0 if field.alias == 'difficulty' else value >= 0
        except AssertionError:
            message = f'Invalid {field.alias}: {value}.'
            logger.error(f'[BlockSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('timestamp')
    def valid_timestamp(cls, value: int):
        """
        Validate timestamp value.

        :param int value: provided timestamp value.
        :return int: validated timestamp value.
        :raise ValueError: if timestamp value is not in milliseconds.
        """
        try:
            assert math.floor(math.log(value, 10) + 1) == BLOCK_TIMESTAMP_LENGTH
        except AssertionError:
            message = f'Invalid timestamp: {value}.'
            logger.error(f'[BlockSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('data')
    def valid_data(cls, value: list):
        """
        Validate transactions data value.

        :param list value: provided data value.
        :return list: validated transactions list data.
        :raise ValueError: if transaction data is invalid.
        """
        from src.client.schemas.transaction import TransactionSchema
        try:
            for transaction_info in value:
                TransactionSchema(**transaction_info)
        except ValidationError as err:
            message = re.sub('\s+',' ', err.json())
            logger.error(f'[BlockSchema] Validation error. {message}')
            raise ValueError(message)
        return value

    @validator('last_hash', 'hash')
    def valid_hash(cls, value: str, values: dict, field: Field):
        """
        Validate hashes values.

        :param str value: provided last_hash or hash values.
        :param dict values: previous fields already validated.
        :param Field field: field name to validate its value.
        :return str: validated last_hash or hash value.
        :raise ValueError: if last_hash or hash values do not meet required conditions.
        """
        match = re.match(r'^(?P<hash>[a-f0-9]{64})$', value)
        if len(value) != BLOCK_HASH_LENGTH or not match:
            message = f'Invalid pattern for {field.alias} value: {value}.'
            logger.error(f'[BlockSchema] Validation error. {message}')
            raise ValueError(message)
        if field.alias == 'hash':
            try:
                assert hex_to_binary(value).startswith('0' * values.get('difficulty'))
                assert value == hash_block(*values.values())
            except AssertionError:
                message = f'Invalid hash: {value}.'
                logger.error(f'[BlockSchema] Validation error. {message}')
                raise ValueError(message)
        return value
