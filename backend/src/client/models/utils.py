# encoding: utf-8

import json
from datetime import datetime
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from src.exceptions import WalletError

# Custom logger for client utils module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


def get_utcnow_timestamp():
    """
    Return UTC current epoch datetime in milliseconds.

    :return int: current datetime timestamp.
    """
    return int(datetime.utcnow().timestamp() * 1000)


def serialize(data: dict):
    """
    Serialize the data.

    :param dict data: data to serialize.
    :return str: stringified data.
    :raise WalletError: on data encoding error.
    """
    try:
        return json.dumps(data)
    except (OverflowError, TypeError) as err:
        message = f'Could not encode data {data}. {err.args[0]}.'
        logger.error(f'[Wallet] Serialization error. {message}')
        raise WalletError(message)
