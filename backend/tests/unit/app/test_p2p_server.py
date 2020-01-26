# encoding: utf-8

import random

import websockets
from aiounittest import async_test
from asynctest import patch as async_patch
from websockets.client import WebSocketClientProtocol as Socket
from websockets.server import WebSocketServer

from src.app.p2p_server import P2PServer
from src.blockchain.models.blockchain import Blockchain
from tests.unit.app.utilities import NodesNetworkMixin


class P2PServerTest(NodesNetworkMixin):

    def setUp(self):
        self.host = '127.0.0.1'
        self.port = 3000
        self.blockchain = Blockchain()
        self.p2p_server = P2PServer(self.blockchain)
        self.p2p_server.bind(self.host, self.port)

    def test_p2p_server_uri(self):
        uri = f'ws://{self.p2p_server.host}:{self.p2p_server.port}'
        self.assertEqual(self.p2p_server.uri, uri)
    
    def test_p2p_server_bind(self):
        host = '127.0.0.1'
        port = self._get_random_port()
        self.assertEqual(self.p2p_server.host, self.host)
        self.assertEqual(self.p2p_server.port, self.port)
        self.p2p_server.bind(host, port)
        self.assertEqual(self.p2p_server.host, host)
        self.assertEqual(self.p2p_server.port, port)

    @async_test
    async def test_p2p_server_start_and_close(self):
        server = await self.p2p_server.start()
        self.assertIsInstance(server, WebSocketServer)
        self.p2p_server.close()

    @async_test
    @async_patch.object(P2PServer, '_add_uris')
    @async_patch.object(P2PServer, '_message_handler')
    async def test_p2p_server_connect_nodes(self, mock_handler, mock_add_uris):
        mock_add_uris.return_value = None
        mock_handler.return_value = None
        nodes = [self.p2p_server.uri]
        self.p2p_server.nodes.uris.add(nodes)
        await self.p2p_server.start()
        await self.p2p_server.connect_nodes(nodes)
        self.assertTrue(mock_add_uris.called)
        self.assertTrue(mock_handler.called)
        self.assertEqual(self.p2p_server.nodes.uris.size, len(nodes))
        self.assertEqual(self.p2p_server.nodes.sockets.size, len(nodes))
        self.p2p_server.close()

    def test_p2p_server_add_uris(self):
        uris = self._generate_uris(random.randint(1, 10))
        self.p2p_server._add_uris(uris)
        self.assertEqual(self.p2p_server.nodes.uris.size, len(uris))

    def test_p2p_server_add_uris_server_listener(self):
        uris = self._generate_uris(random.randint(1, 10))
        uris.append(self.p2p_server.uri)
        self.p2p_server._add_uris(uris.copy())
        self.assertEqual(self.p2p_server.nodes.uris.size, len(uris) - 1)

    def test_p2p_server_add_socket(self):
        sockets = [Socket() for _ in range(random.randint(1, 10))]
        self.p2p_server._add_socket(sockets)
        self.assertEqual(self.p2p_server.nodes.sockets.size, len(sockets))

    def test_p2p_server_clear_sockets(self):
        sockets = [Socket() for _ in range(random.randint(1, 10))]
        self.p2p_server._add_socket(sockets)
        self.assertEqual(self.p2p_server.nodes.sockets.size, len(sockets))
        self.p2p_server._clear_sockets()
        self.assertEqual(self.p2p_server.nodes.sockets.size, 0)

    def test_p2p_server_set_local_address(self):
        host = '127.0.0.1'
        port = self._get_random_port()
        self.assertEqual(self.p2p_server.host, self.host)
        self.assertEqual(self.p2p_server.port, self.port)
        self.p2p_server._set_local_address(host, port)
        self.assertEqual(self.p2p_server.host, host)
        self.assertEqual(self.p2p_server.port, port)

    @async_test
    async def test_p2p_server_get_remote_address(self):
        uri = self.p2p_server.uri
        await self.p2p_server.start()
        async with websockets.connect(uri) as socket:
            host, port = self.p2p_server._get_remote_address(socket)
            self.assertIn(host, uri)
            self.assertIn(str(port), uri)
        self.p2p_server.close()

    @async_test
    @async_patch.object(P2PServer, '_message_handler')
    async def test_p2p_server_set_remote_address(self, mock_handler):
        mock_handler.return_value = None
        nodes = [self.p2p_server.uri]
        self.p2p_server.nodes.uris.add(nodes)
        await self.p2p_server.start()
        await self.p2p_server.connect_nodes(nodes)
        self.assertTrue(mock_handler.called)
        async for socket in self.p2p_server.nodes.sockets:
            host, port = self.p2p_server._get_remote_address(socket)
            self.assertEqual(host, socket.remote_address[0])
            self.assertEqual(port, socket.remote_address[1])
        self.p2p_server.close()

    @async_test
    @async_patch.object(P2PServer, '_message_handler')
    async def test_p2p_server_send_node(self, mock_handler):
        mock_handler.return_value = None
        nodes = [self.p2p_server.uri]
        self.p2p_server.nodes.uris.add(nodes)
        await self.p2p_server.start()
        await self.p2p_server._connect_socket(self.p2p_server._send_node, nodes[0])
        self.assertTrue(mock_handler.called)
        self.p2p_server.close()

    @async_test
    @async_patch.object(Blockchain, 'deserialize')
    async def test_p2p_server_send_chain(self, mock_deserialize):
        mock_deserialize.return_value = None
        nodes = [self.p2p_server.uri]
        self.p2p_server.nodes.uris.add(nodes)
        await self.p2p_server.start()
        await self.p2p_server._connect_socket(self.p2p_server._send_chain, nodes[0])
        self.assertTrue(mock_deserialize.called)
        self.p2p_server.close()

    @async_test
    @async_patch.object(Blockchain, 'deserialize')
    async def test_p2p_server_broadcast(self, mock_deserialize):
        mock_deserialize.return_value = None
        nodes = [self.p2p_server.uri]
        self.p2p_server.nodes.uris.add(nodes)
        await self.p2p_server.start()
        await self.p2p_server.broadcast()
        self.assertTrue(mock_deserialize.called)
        self.p2p_server.close()   
