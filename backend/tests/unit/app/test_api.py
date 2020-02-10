# encoding: utf-8

import asyncio
import random
from unittest.mock import patch

from starlette.testclient import TestClient

from src.app.api import app
from src.blockchain.models.block import Block
from tests.unit.logging import LoggingMixin


class ApiTest(LoggingMixin):

    def setUp(self):
        self.client = TestClient(app)
    
    def test_api_get_root_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Blockchain app is running")

    def test_api_get_blockchain_route(self):
        response = self.client.get("/blockchain")
        self.assertEqual(response.status_code, 200)
        self.assertIn('blockchain', response.json())
        self.assertIn('chain', response.json().get('blockchain'))
        chain = response.json().get('blockchain').get('chain')
        self.assertEqual(len(chain), app.blockchain.length)

    @patch('src.app.api.app.p2p_server.broadcast')
    def test_api_get_mine_block_route(self, mock_broadcast):
        mock_broadcast.return_value = asyncio.Future()
        mock_broadcast.return_value.set_result(None)
        response = self.client.get("/mine")
        self.assertTrue(mock_broadcast.called)
        self.assertEqual(response.status_code, 200)
        self.assertIn('new_block', response.json())
        block_info = response.json().get('new_block')
        self.assertEqual(Block.create(**block_info), app.blockchain.last_block)

    def test_api_post_transact_route(self):
        recipient = "recipient"
        amount = random.uniform(0, 100)
        response = self.client.post("/transact", json={"recipient": recipient, "amount": amount})
        self.assertEqual(response.status_code, 200)
        self.assertIn('transaction', response.json())
        transaction = response.json().get('transaction')
        self.assertTrue(all([key in transaction for key in ('uuid', 'output', 'input')]))
        self.assertEqual(transaction.get('output').get(recipient), amount)
