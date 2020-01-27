# encoding: utf-8

import random

from aiounittest import async_test
from websockets.client import WebSocketClientProtocol as Socket

from src.app.nodes import NodesNetwork
from tests.unit.app.utilities import NodesNetworkMixin


class NodesNetworkTest(NodesNetworkMixin):

    def setUp(self):
        self.nodes = NodesNetwork()
        self.uris = self._generate_uris(10)
        self.sockets = [Socket() for _ in range(random.randint(1, 10))]

    def test_nodes_string_representation(self):
        self.nodes.uris.add(self.uris)
        self.nodes.sockets.add(self.sockets)
        self.assertTrue(all([uri in str(self.nodes) for uri in self.uris]))
        self.assertTrue(all([str(socket) in str(self.nodes) for socket in self.sockets]))

    def test_nodes_has_uris(self):
        self.assertTrue(hasattr(self.nodes, 'uris'))

    def test_nodes_has_sockets(self):
        self.assertTrue(hasattr(self.nodes, 'sockets'))

    def test_nodes_add(self):
        self.assertEqual(self.nodes.uris.size, 0)
        self.assertEqual(self.nodes.sockets.size, 0)
        self.nodes.uris.add(self.uris)
        self.assertEqual(self.nodes.uris.size, len(self.uris))
        self.assertEqual(self.nodes.sockets.size, 0)

    def test_nodes_add_repeat_item(self):
        self.nodes.uris.add(self.uris)
        self.assertEqual(self.nodes.uris.size, len(self.uris))
        uri = random.choice(self.uris)
        self.nodes.uris.add(uri)
        self.assertEqual(self.nodes.uris.size, len(self.uris))

    def test_nodes_coherent(self):
        self.assertEqual(self.nodes.uris.size, 0)
        self.assertEqual(self.nodes.sockets.size, 0)
        self.assertTrue(self.nodes.coherent)
        self.nodes.uris.add(self.uris)
        self.assertEqual(self.nodes.uris.size, len(self.uris))
        self.assertEqual(self.nodes.sockets.size, 0)
        self.assertFalse(self.nodes.coherent)

    def test_nodes_array(self):
        self.assertIsInstance(self.nodes.uris.array, list)
        self.assertIsInstance(self.nodes.sockets.array, list)
        self.nodes.uris.add(self.uris)
        self.assertEqual(len(self.nodes.uris.array), self.nodes.uris.size)
        self.assertTrue(all([uri in self.nodes.uris.array for uri in self.uris]))

    def test_nodes_clear(self):
        self.nodes.uris.add(self.uris)
        self.assertEqual(self.nodes.uris.size, len(self.uris))
        self.nodes.uris.clear()
        self.assertEqual(self.nodes.uris.size, 0)

    def test_nodes_contains(self):
        self.nodes.uris.add(self.uris)
        uri = random.choice(self.uris)
        self.assertTrue(uri in self.nodes.uris)

    @async_test
    async def test_nodes_async_iteration(self):
        self.nodes.uris.add(self.uris)
        async for uri in self.nodes.uris:
            self.assertTrue(uri in self.nodes.uris)
