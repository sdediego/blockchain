# encoding: utf-8

import asyncio
import json
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join
from typing import Union

import websockets
from websockets.client import WebSocketClientProtocol as Socket
from websockets.exceptions import WebSocketException
from websockets.server import WebSocketServer

from src.app.nodes import NodesNetwork
from src.app.utils import parse, stringify
from src.blockchain.models.blockchain import Blockchain
from src.client.models.transaction import Transaction
from src.client.models.transactions_pool import TransactionsPool
from src.config.settings import CHANNELS, HEARTBEAT_RATE
from src.exceptions import P2PServerError

# Custom logger for p2p server class module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class P2PServer(object):
    """
    Peer-to-peer socket server to exchange and keep a unique blockchain
    ledger and mine new blocks. Each node keeps a local blockchain copy
    that is synchronized with the rest of the network every time a new
    block is mined.
    Each network node keeps track of the rest of the network nodes.
    """

    def __init__(self, blockchain: Blockchain, transactions_pool: TransactionsPool):
        """
        Create a new P2PServer instance.

        :param Blockchain blockchain: local copy of the blockchain.
        """
        self.host = None
        self.port = None
        self.server = None
        self.blockchain = blockchain
        self.transactions_pool = transactions_pool
        self.nodes = NodesNetwork()

    def __str__(self):
        """"
        Represent class instance via params string.

        :return str: instance representation.
        """
        return ('P2PServer('
            f'host: {self.host}, '
            f'port: {self.port}, '
            f'server uri: {self.uri})')

    @property
    def uri(self):
        """
        Get socket server uri (uniform resource identifier).
        The server uri will be shared with the rest of the
        network nodes to make requests to the server.
        """
        return f'ws://{self.host}:{self.port}'

    def bind(self, host: str, port: int):
        """
        Set socket server host and port.

        :param str host: server host name.
        :param int port: server port.
        """
        self._set_local_address(host, port)

    async def start(self, host: str = None, port: int = None):
        """
        Start socket server that accepts incoming connections from socket clients.
        Socket requests will be handled and then connection will be closed.

        :param str host: server host name.
        :param int port: server port.
        :return WebSocketServer: socket server.
        """
        if not self.host or not self.port: self.bind(host, port)
        self.server = await websockets.serve(self._listen, self.host, self.port)
        return self.server

    def close(self):
        """
        Close socket server.
        Stop accepting connections from socket clients.
        """
        self.server.close()

    async def connect_nodes(self, uris: Union[str, list] = None):
        """
        Register network nodes uris to be able to communicate.
        Send local socket server uri to the rest of the nodes.

        :param [str, list] uris: uris of the rest of the network nodes.
        """
        if uris: self.add_uris(uris)
        await self._connect_sockets(self._send_node, True)

    async def heartbeat(self):
        """
        Run periodic signal to synchronize all the network nodes.

        :return func: heartbeat daemon.
        """
        async def _heartbeat():
            while True:
                await self._synchronize()
                await asyncio.sleep(HEARTBEAT_RATE)
        return await _heartbeat()

    async def _listen(self, socket: Socket, path: str):
        """
        Listen to the incoming socket connections to handle them.

        :param Socket socket: incoming socket client.
        :param str path: file system path to the socket.
        """
        logger.info(f'[P2PServer] Socket received: {self._get_remote_address(socket)}.')
        await self._message_handler(socket)

    def add_uris(self, uris: Union[str, list]):
        """
        Register unique uris of the rest of the network nodes servers.

        :param [str, list] uris: network nodes uris.
        """
        if isinstance(uris, str) and uris == self.uri: return
        if isinstance(uris, list) and self.uri in uris: uris.remove(self.uri)
        self.nodes.uris.add(uris)

    def _add_socket(self, socket: Socket):
        """
        Register open socket connections with the rest of the network
        nodes servers.

        :param Socket socket: opened socket clients with the network nodes.
        """
        self.nodes.sockets.add(socket)

    def _clear_sockets(self):
        """
        Clear socket client connections with the rest of the nodes.
        """
        self.nodes.sockets.clear()

    def _set_local_address(self, host: str, port: int):
        """
        Set socket server local host and port.

        :param str host: server host name.
        :param int port: server port.
        """
        self.host, self.port = host, port

    def _get_remote_address(self, socket: Socket):
        """
        Get socket remote address.

        :param Socket socket: incoming socket client.
        :param tuple: socket remote IP address and port.
        """
        return socket.remote_address

    async def broadcast_chain(self):
        """
        Broadcast local chain to the rest of the network nodes.
        After a new block is mined and added to the local chain it is broadcasted
        to the rest of the nodes and if valid replaced as the new blockchain instance
        for the entire network.
        """
        logger.info(f'[P2PServer] Broadcasting chain to network nodes.')
        await self._connect_sockets(self._send_chain, False)
        message = f'Network nodes broadcasted: {self.nodes.uris.size}.'
        logger.info(f'[P2PServer] Broadcast finished. {message}')

    async def broadcast_transaction(self, transaction: Transaction):
        """
        Broadcast new transaction to the rest of the network nodes.
        After a new transaction is created it is broadcasted to the rest of the
        network nodes.
        """
        logger.info(f'[P2PServer] Broadcasting transaction to network nodes.')
        await self._connect_sockets(self._send_transaction, False, transaction)
        message = f'Network nodes broadcasted: {self.nodes.uris.size}.'
        logger.info(f'[P2PServer] Broadcast finished. {message}')

    async def _synchronize(self):
        """
        Synchronize all the network nodes.
        Synchronization between nodes is done by sharing known nodes with each other.
        """
        message = {'channel': CHANNELS.get('sync'), 'content': self.nodes.uris.array}
        self._clear_sockets()
        await self._connect_sockets(self._send, True, message)
        if not self.nodes.coherent:
            warning_msg = f'Uris: {self.nodes.uris.size}, Sockets: {self.nodes.sockets.size}.'
            logger.warning(f'[P2PServer] Nodes incoherence. {warning_msg}')

    async def _connect_sockets(self, callback, register: bool, *args):
        """
        Create multiple socket client connections to all the known socket servers
        registered by the local node.

        :param callback: operation to perform after connection is opened.
        :param bool register: wether if register socket connection.
        """
        async for uri in self.nodes.uris:
            await self._connect_socket(callback, uri, register, *args)

    async def _connect_socket(self, callback, uri: str, register: bool = False, *args):
        """
        Create a socket client connection to the socket server provided uri.

        :param callback: operation to perform after connection is opened.
        :param str uri: socket server node uri to connect to.
        :param bool register: wether if register socket connection.
        """
        try:
            async with websockets.connect(uri) as socket:
                if register: self._add_socket(socket)
                await callback(socket, *args)
        except (ConnectionError, WebSocketException):
            warning_msg = f'Not connected to uri: {uri}.'
            logger.warning(f'[P2PServer] Connection error. {warning_msg}')

    async def _send_node(self, socket: Socket):
        """
        Send message with local server uri data over a socket connection.

        :param Socket socket: outgoing socket client.
        """
        message = {'channel': CHANNELS.get('node'), 'content': self.uri}
        await self._send(socket, message)

    async def _send_chain(self, socket: Socket):
        """
        Send message with local blockchain data over a socket connection.

        :param Socket socket: outgoing socket client.
        """
        message = {'channel': CHANNELS.get('chain'), 'content': self.blockchain.serialize()}
        await self._send(socket, message)

    async def _send_transaction(self, socket: Socket, transaction: Transaction):
        """
        Send message with new transaction data over a socket connection.

        :param Socket socket: outgoing socket client.
        :param Transaction transaction: transaction instance to send.
        """
        message = {'channel': CHANNELS.get('transact'), 'content': transaction.serialize()}
        await self._send(socket, message)

    async def _send(self, socket: Socket, message: dict):
        """
        Send message with data over a socket connection.

        :param Socket socket: outgoing socket client.
        :param dict message: message with no serialized data to be sent.
        """
        await socket.send(stringify(message))

    async def _message_handler(self, socket: Socket):
        """
        Handle the incoming socket client and process the message data.
        It exits normally when the connection is closed.

        :param Socket socket: incoming socket client.
        """
        async for message in socket:
            data = parse(message)
            channel = data.get('channel')
            if channel == CHANNELS.get('node'):
                uri = data.get('content')
                info_msg = f'Uri listed. {uri}.'
                logger.info(f'[P2PServer] Node received. {info_msg}')
                self.add_uris(uri)
                await self._connect_socket(self._send_chain, uri)
            elif channel == CHANNELS.get('sync'):
                uris = data.get('content')
                self.add_uris(uris)
                info_msg = f'Total uris: {self.nodes.uris.array}.'
                logger.info(f'[P2PServer] Synchronization finished. {info_msg}')
            elif channel == CHANNELS.get('chain'):
                chain = data.get('content')
                logger.info(f'[P2PServer] Chain received. {chain}.')
                blockchain = Blockchain.deserialize(chain)
                self.blockchain.set_valid_chain(blockchain.chain)
                self.transactions_pool.clear_pool(self.blockchain)
            elif channel == CHANNELS.get('transact'):
                transaction_info = data.get('content')
                logger.info(f'[P2PServer] Transaction received. {transaction_info}.')
                transaction = Transaction.deserialize(transaction_info)
                self.transactions_pool.add_transaction(transaction)
            else:
                error_msg = f'Unknown channel received: {channel}.'
                logger.error(f'[P2PServer] Channel error. {error_msg}')
