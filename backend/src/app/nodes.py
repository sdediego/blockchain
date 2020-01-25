# encoding: utf-8

from typing import Union

from websockets.client import WebSocketClientProtocol as Socket


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
            raise StopAsyncIteration
        self.index += 1
        return item

    def __contains__(self, item: Union[str, Socket]):
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
            self.sequence.add(item)

    def clear(self):
        self.sequence.clear()
        self.index = 0


class NodesNetwork(object):

    def __init__(self):
        self.uris = AsyncSet('uris')
        self.sockets = AsyncSet('sockets')

    @property
    def coherent(self):
        return self.uris.size == self.sockets.size
