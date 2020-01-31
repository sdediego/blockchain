# encoding: utf-8

import json
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from src.exceptions import WalletError

# Custom logger for utils module
fileConfig(join(dirname(dirname(dirname(__file__))), 'config', 'logging.cfg'))
logger = getLogger(__name__)


def serialize(data):
    try:
        return json.dumps(data)
    except (OverflowError, TypeError) as err:
        message = f'Could not encode data {data}. {err.args[0]}.'
        logger.error(f'[Wallet] Serialization error. {message}')
        raise WalletError(message)
