# encoding: utf-8

import asyncio
import random
import uuid
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

    @patch('src.app.api.app.p2p_server.broadcast_chain')
    @patch('src.app.api.app.transactions_pool.clear_pool')
    def test_api_get_mine_block_route(self, mock_clear_pool, mock_broadcast_chain):
        mock_broadcast_chain.return_value = asyncio.Future()
        mock_broadcast_chain.return_value.set_result(None)
        mock_clear_pool.return_value = True
        response = self.client.get("/mine")
        self.assertTrue(mock_broadcast_chain.called)
        self.assertTrue(mock_clear_pool.called)
        self.assertEqual(response.status_code, 200)
        self.assertIn('block', response.json())
        block_info = response.json().get('block')
        self.assertEqual(Block.create(**block_info), app.blockchain.last_block)

    @patch('src.app.api.app.p2p_server.broadcast_transaction')
    def test_api_post_transact_route(self, mock_broadcast_transaction):
        mock_broadcast_transaction.return_value = asyncio.Future()
        mock_broadcast_transaction.return_value.set_result(None)
        recipient = uuid.uuid4().hex
        amount = random.uniform(0, 25)
        response = self.client.post("/transact", json={"recipient": recipient, "amount": amount})
        self.assertTrue(mock_broadcast_transaction.called)
        self.assertEqual(response.status_code, 200)
        self.assertIn('transaction', response.json())
        transaction = response.json().get('transaction')
        self.assertTrue(all([key in transaction for key in ('uuid', 'output', 'input')]))
        self.assertEqual(transaction.get('output').get(recipient), amount)

    def test_api_get_balance_route(self):
        response = self.client.get("/balance")
        self.assertEqual(response.status_code, 200)
        self.assertIn('address', response.json())
        self.assertIn('balance', response.json())
        balance = response.json().get('balance')
        self.assertEqual(balance, 0)
