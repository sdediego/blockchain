# encoding: utf-8

import hashlib
import json
from datetime import datetime
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from src.exceptions import BlockError

# Custom logger for utils module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


def get_utcnow_timestamp():
    """
    Return UTC current epoch datetime in milliseconds.

    :return int: current datetime timestamp.
    """
    return int(datetime.utcnow().timestamp() * 1000)


def hash_block(*args: tuple):
    """
    Create a unique 256-bit hash value (64 characters length) from the rest
    of the block attributes values with sha256 cryptographic hash function.

    :param tuple args: sequence with all block attributes except hash.
    :return str: block unique hash attribute.
    :raise BlockError: on block data encoding error.
    """
    try:
        stringified = sorted(map(lambda arg: json.dumps(arg), args))
    except (OverflowError, TypeError) as err:
        message = f'Could not encode block data to generate hash. {err.args[0]}.'
        logger.error(f'[Block] Stringify error. {message}')
        raise BlockError(message)
    joined = ''.join(stringified)
    return hashlib.sha256(joined.encode('utf-8')).hexdigest()


def hex_to_binary(hash: str):
    """
    Convert hexadecimal hash string to binary.

    :param str hash: hexadecimal number representing hash string.
    :return : converted hexadecimal hash string to binary.
    """
    return f'{int(hash, base=16):0>256b}'
