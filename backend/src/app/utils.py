# encoding: utf-8

import json
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from src.exceptions import P2PServerError

# Custom logger for utils module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


def stringify(message: dict):
    """
    Stringify the message to be able to send the data over
    the network to the rest of the peer nodes.

    :param dict message: message with data to transfer.
    :return str: message data in string format.
    """
    try:
        return json.dumps(message)
    except (OverflowError, TypeError) as err:
        message = f'Could not encode message data. {err.args[0]}.'
        logger.error(f'[P2PServer] Stringify error. {message}')
        raise P2PServerError(message)


def parse(message: str):
    """
    Recover the original data from the provided stringified message.

    :param str message: stringified message.
    :return dict: parsed message with data.
    """
    try:
        return json.loads(message)
    except (OverflowError, TypeError) as err:
        message = f'Could not decode message data. {err.args[0]}.'
        logger.error(f'[P2PServer] Parse error. {message}')
        raise P2PServerError(message)
