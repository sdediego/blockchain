# encoding: utf-8

import websockets
from websockets.client import WebSocketClientProtocol as Socket

import asyncio
import json
from functools import wraps
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join
from typing import Union

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
        self.blockchain = blockchain
        self.nodes = NodesNetwork()

    @property
    def uri(self):
        return f'ws://{self.host}:{self.port}'

    def bind(self,  host:str, port: int):
        self._set_address(host, port)

    async def set_nodes(self, uris: Union[str, list]):
        self._add_uris(uris)
        await self._connect()

    async def start(self, host: str = None, port: int = None):
        self._set_address(host, port) if not self.host or not self.port else None
        return await websockets.serve(self._listen, self.host, self.port)

    async def _listen(self, socket: Socket, path: str):
        logger.info(f'[P2PServer] Socket received: {socket.remote_address}.')
        await self._message_handler(socket)

    def _add_uris(self, uris: Union[str, list]):
        self.nodes.uris.add(uris)

    def _set_address(self, host: str, port: int):
        self.host, self.port = host, port

    async def _connect(self):
        async for uri in self.nodes.uris:
            async with websockets.connect(uri) as socket:
                self._add_socket(socket)
                await self._notify(socket)

    def _add_socket(self, socket: Socket):
        self.nodes.sockets.add(socket)

    async def _notify(self, socket: Socket):
        message = {'event': 'notification', 'content': self.uri}
        await self._send(socket, message)

    async def _message_handler(self, socket: Socket):
        async for message in socket:
            data = self._parse(message)
            event = data.get('event')
            if event == 'notification':
                uri = data.get('content')
                self._add_uris(uri)
                logger.info(f'[P2PServer] Node listed. {uri}')
            else:
                pass

    async def _send(self, socket: Socket, message: dict):
        await socket.send(self._stringify(message))

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
