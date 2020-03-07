# encoding: utf-8

import asyncio
import random
import uuid
from unittest.mock import patch

from starlette.testclient import TestClient

from src.app.api import app
from src.blockchain.models.block import Block
from src.blockchain.models.blockchain import Blockchain
from tests.unit.blockchain.utilities import BlockchainMixin


class ApiTest(BlockchainMixin):

    def setUp(self):
        super(ApiTest, self).setUp()
        chain_length = random.randint(5, 10)
        chain = self._generate_valid_chain(chain_length)
        app.blockchain = Blockchain(chain)
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
    @patch('src.client.models.transaction.Transaction.is_valid_schema')
    def test_api_post_transact_route(self, mock_is_valid_schema, mock_broadcast_transaction):
        mock_broadcast_transaction.return_value = asyncio.Future()
        mock_broadcast_transaction.return_value.set_result(None)
        mock_is_valid_schema.return_value = True
        recipient = uuid.uuid4().hex
        amount = random.uniform(0, 25)
        response = self.client.post("/transact", json={"recipient": recipient, "amount": amount})
        self.assertTrue(mock_broadcast_transaction.called)
        self.assertTrue(mock_is_valid_schema.called)
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

    def test_api_get_addresses_route(self):
        response = self.client.get("/addresses")
        self.assertEqual(response.status_code, 200)
        self.assertIn('addresses', response.json())
        addresses = response.json().get('addresses')
        self.assertIsInstance(addresses, list)
        self.assertTrue(all([uuid.UUID(hex=address) for address in addresses]))
