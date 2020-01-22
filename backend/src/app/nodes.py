# encoding: utf-8

from websockets.client import WebSocketClientProtocol as Socket

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join
from typing import Union

# Custom logger for nodes module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class AsyncSet(set):

    def __init__(self, name: str):
        super(AsyncSet, self).__init__()
        self.name = name
        self.sequence = set()
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = None
        try:
            item = self.array[self.index]
        except IndexError:
            self.index = 0
            message = f'{self.name.capitalize()} processed: {self.size}.'
            logger.info(f'[NodesNetwork] Processing finished. {message}')
            raise StopAsyncIteration
        self.index += 1
        return item

    def __contains__(self, item):
        return item in self.sequence

    @property
    def array(self):
        return list(self.sequence)

    @property
    def size(self):
        return len(self.sequence)

    def add(self, items: Union[str, Socket, list]):
        items = items if isinstance(items, list) else [items]
        for item in items:
            item = item.strip() if isinstance(item, str) else item
            self.sequence.add(item)
        logger.info(f'[NodesNetwork] {self.name.capitalize()} added: {len(items)}.')
        logger.info(f'[NodesNetwork] Total {self.name.capitalize()}: {self.size}.')


class NodesNetwork(object):

    def __init__(self):
        self.uris = AsyncSet('uris')
        self.sockets = AsyncSet('sockets')
