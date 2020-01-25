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

from src.app.nodes import NodesNetwork
from src.blockchain.models.blockchain import Blockchain
from src.config.settings import CHANNELS, HEARTBEAT_RATE
from src.exceptions import P2PServerError

# Custom logger for p2p_server module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class P2PServer(object):

    def __init__(self, blockchain: Blockchain):
        self.host = None
        self.port = None
        self.server = None
        self.blockchain = blockchain
        self.nodes = NodesNetwork()

    @property
    def uri(self):
        return f'ws://{self.host}:{self.port}'

    def bind(self,  host: str, port: int):
        self._set_local_address(host, port)

    async def start(self, host: str = None, port: int = None):
        if not self.host or not self.port: self.bind(host, port)
        self.server = await websockets.serve(self._listen, self.host, self.port)
        return self.server

    def close(self):
        self.server.close()

    async def connect_nodes(self, uris: Union[str, list]):
        self._add_uris(uris)
        await self._connect_sockets(self._send_node, True)

    async def heartbeat(self):
        async def _heartbeat():
            while True:
                await self._synchronize()
                await asyncio.sleep(HEARTBEAT_RATE)
        return await _heartbeat()

    async def _listen(self, socket: Socket, path: str):
        logger.info(f'[P2PServer] Socket received: {self._get_remote_address(socket)}.')
        await self._message_handler(socket)

    def _add_uris(self, uris: Union[str, list]):
        if isinstance(uris, str) and uris == self.uri: return
        if isinstance(uris, list) and self.uri in uris: uris.remove(self.uri)
        self.nodes.uris.add(uris)

    def _add_socket(self, socket: Socket):
        self.nodes.sockets.add(socket)

    def _clear_sockets(self):
        self.nodes.sockets.clear()

    def _set_local_address(self, host: str, port: int):
        self.host, self.port = host, port

    def _get_remote_address(self, socket: Socket):
        return socket.remote_address

    async def broadcast(self):
        logger.info(f'[P2PServer] Broadcasting to network nodes.')
        await self._connect_sockets(self._send_chain, False)
        message = f'Network nodes broadcasted: {self.nodes.uris.size}.'
        logger.info(f'[P2PServer] Broadcast finished. {message}')

    async def _connect_sockets(self, callback, register: bool, *args):
         async for uri in self.nodes.uris:
             await self._connect_socket(callback, uri, register, *args)

    async def _connect_socket(self, callback, uri: str, register: bool = False, *args):
        try:
            async with websockets.connect(uri) as socket:
                if register: self._add_socket(socket)
                await callback(socket, *args)
        except (ConnectionError, WebSocketException):
            warning_msg = f'Not connected to uri: {uri}'
            logger.warning(f'[P2PServer] Connection error. {warning_msg}.')

    async def _synchronize(self):
        message = {'channel': CHANNELS.get('sync'), 'content': self.nodes.uris.array}
        self._clear_sockets()
        await self._connect_sockets(self._send, True, message)
        if not self.nodes.coherent:
            warning_msg = f'Uris: {self.nodes.uris.size}, Sockets: {self.nodes.sockets.size}.'
            logger.warning(f'[P2PServer] Nodes incoherence. {warning_msg}')

    async def _send_node(self, socket: Socket):
        message = {'channel': CHANNELS.get('node'), 'content': self.uri}
        await self._send(socket, message)

    async def _send_chain(self, socket: Socket):
        message = {'channel': CHANNELS.get('chain'), 'content': self.blockchain.serialize()}
        await self._send(socket, message)

    async def _send(self, socket: Socket, message: dict):
        await socket.send(self._stringify(message))

    async def _message_handler(self, socket: Socket):
        async for message in socket:
            data = self._parse(message)
            channel = data.get('channel')
            if channel == CHANNELS.get('node'):
                uri = data.get('content')
                info_msg = f'Uri listed. {uri}.'
                logger.info(f'[P2PServer] Node received. {info_msg}')
                self._add_uris(uri)
                await self._connect_socket(self._send_chain, uri)
            elif channel == CHANNELS.get('sync'):
                uris = data.get('content')
                self._add_uris(uris)
                info_msg = f'Total uris: {self.nodes.uris.array}.'
                logger.info(f'[P2PServer] Synchronization finished. {info_msg}')
            elif channel == CHANNELS.get('chain'):
                chain = data.get('content')
                logger.info(f'[P2PServer] Chain received. {chain}.')
                blockchain = Blockchain.deserialize(chain)
                self.blockchain.set_valid_chain(blockchain.chain)
            else:
                error_msg = f'Unknown channel received: {channel}.'
                logger.error(f'[P2PServer] Channel error. {error_msg}')

    def _stringify(self, message: dict):
        try:
            return json.dumps(message)
        except (OverflowError, TypeError) as err:
            message = f'Could not encode message. {err.args[0]}.'
            logger.error(f'[P2PServer] Stringify error. {message}')
            raise P2PServerError(message)

    def _parse(self, message: str):
        try:
            return json.loads(message)
        except (OverflowError, TypeError) as err:
            message = f'Could not decode message data. {err.args[0]}.'
            logger.error(f'[P2PServer] Parse error. {message}')
            raise P2PServerError(message)
