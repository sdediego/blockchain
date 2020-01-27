# encoding: utf-8

from typing import Union

from websockets.client import WebSocketClientProtocol as Socket


class AsyncSet(set):
    """
    Extended set object that allows asynchronous operations
    over the contained sequence.
    """

    def __init__(self, name: str):
        """
        Create a new AsyncSet instance.

        :param str name: name of the set.
        """
        super(AsyncSet, self).__init__()
        self.name = name
        self.sequence = set()
        self.index = 0

    def __aiter__(self):
        """
        Generates an asynchronous iterator.

        :return AsyncSet: asynchronous set instance.
        """
        return self

    async def __anext__(self):
        """
        Returns the next element for the asynchronous iterator.

        :return [str, Socket]: next element of the set.
        """
        item = None
        try:
            item = self.array[self.index]
        except IndexError:
            self.index = 0
            raise StopAsyncIteration
        self.index += 1
        return item

    def __contains__(self, item: Union[str, Socket]):
        """
        Checks set membership of an element.

        :param [str, Socket] item: element to check membership.
        :return bool: wether if the set contains the element.
        """
        return item in self.sequence

    @property
    def array(self):
        """
        Get a list from the contained set.

        :return list: indexable sequence from set.
        """
        return list(self.sequence)

    @property
    def size(self):
        """
        Get the set size.

        :return int: number of elements contained in the set.
        """
        return len(self.sequence)

    def add(self, items: Union[str, Socket, list]):
        """
        Insert new element into the set.
        Only unique elements will be added to the set.

        :params [str, Socket, list] items: elements to be added.
        """
        items = items if isinstance(items, list) else [items]
        for item in items:
            self.sequence.add(item)

    def clear(self):
        """
        Remove all the elements from the set and reset index.
        """
        self.sequence.clear()
        self.index = 0


class NodesNetwork(object):
    """
    Information storage of all the nodes that join the network.
    The nodes collect the information in a set of the socket uris
    to make the connections between the nodes and a set of the
    open socket connections.
    """

    def __init__(self):
        """
        Create a new NodesNetwork instance.
        """
        self.uris = AsyncSet('uris')
        self.sockets = AsyncSet('sockets')

    def __str__(self):
        """"
        Represent class instance via params string.

        :return str: instance representation.
        """
        return ('NodesNetwork('
            f'uris: {self.uris.array}, '
            f'sockets: {self.sockets.array})')

    @property
    def coherent(self):
        """
        Check the coherence between registered uris and sockets.

        :return bool: wether if uris and sockets sizes are equal.
        """
        return self.uris.size == self.sockets.size
