# encoding: utf-8

import asyncio
import json
from functools import wraps
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join
from typing import Union

import websockets
from websockets.client import WebSocketClientProtocol as Socket
from websockets.exceptions import WebSocketException

from src.app.nodes import NodesNetwork
from src.blockchain.models.blockchain import Blockchain
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
        await self._connect()

    async def _listen(self, socket: Socket, path: str):
        logger.info(f'[P2PServer] Socket received: {self._get_remote_address(socket)}.')
        await self._message_handler(socket)

    async def _connect(self):
        async for uri in self.nodes.uris:
            async with websockets.connect(uri) as socket:
                self._add_socket(socket)
                await self._notify(socket)

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
        async for uri in self.nodes.uris:
            async with websockets.connect(uri) as socket:
                await self._send_chain(socket)
        message = f'Network nodes broadcasted: {self.nodes.uris.size}.'
        logger.info(f'[P2PServer] Broadcast finished. {message}')

    async def _notify(self, socket: Socket):
        message = {'event': 'notification', 'content': self.uri}
        await self._send(socket, message)

    async def _send_chain(self, socket: Socket):
        logger.info(f'[P2PServer] Sending chain to {self._get_remote_address(socket)}.')
        message = {'event': 'blockchain', 'content': self.blockchain.serialize()}
        await self._send(socket, message)

    async def _send(self, socket: Socket, message: dict):
        await socket.send(self._stringify(message))

    async def _message_handler(self, socket: Socket):
        async for message in socket:
            data = self._parse(message)
            event = data.get('event')
            if event == 'notification':
                uri = data.get('content')
                self._add_uris(uri)
                info_msg = f'Uri listed. {uri}.'
                logger.info(f'[P2PServer] Notification received. {info_msg}')
            elif event == 'synchronization':
                uris = data.get('content')
                self._add_uris(uris)
                info_msg = f'Total uris: {self.nodes.uris.array}.'
                logger.info(f'[P2PServer] Synchronization finished. {info_msg}')
            elif event == 'blockchain':
                chain = data.get('content')
                blockchain = Blockchain.deserialize(chain)
                logger.info(f'[Blockchain] Blockchain recieved. {chain}.')
                self.blockchain.set_valid_chain(blockchain.chain)
            else:
                pass

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

    async def heartbeat(self):
        async def _heartbeat():
            while True:
                await self._synchronize()
                await asyncio.sleep(10)
        return await _heartbeat()

    async def _synchronize(self):
        message = {'event': 'synchronization', 'content': self.nodes.uris.array}
        self._clear_sockets()
        async for uri in self.nodes.uris:
            try:
                async with websockets.connect(uri) as socket:
                    self._add_socket(socket)
                    await self._send(socket, message)
            except (ConnectionError, WebSocketException):
                error_msg = f'Not connected to uri: {uri}'
                logger.error(f'[P2PServer] Connection error. {error_msg}.')
        if not self.nodes.coherent:
            warning_msg = f'Uris: {self.nodes.uris.size}, Sockets: {self.nodes.sockets.size}.'
            logger.warning(f'[P2PServer] Nodes incoherence. {warning_msg}')
