# encoding: utf-8

from unittest import TestCase

from starlette.testclient import TestClient

from src.app.api import app
from src.blockchain.models.block import Block


class ApiTest(TestCase):

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

    def test_api_get_mine_block_route(self):
        response = self.client.get("/mine") 
        self.assertEqual(response.status_code, 200)
        self.assertIn('new_block', response.json())
        block_info = response.json().get('new_block')
        self.assertEqual(Block.create(**block_info), app.blockchain.last_block)
