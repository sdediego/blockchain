# encoding: utf-8

import random
from unittest.mock import Mock, patch

from src.blockchain.models.block import Block
from src.blockchain.models.blockchain import Blockchain
from src.client.models.transaction import Transaction
from src.client.models.wallet import Wallet
from src.exceptions import BlockchainError
from tests.unit.blockchain.utilities import BlockchainMixin


class BlockchainTest(BlockchainMixin):

    def setUp(self):
        super(BlockchainTest, self).setUp()
        self.chain_length = random.randint(5, 10)
        self.valid_chain = self._generate_valid_chain(self.chain_length)
        self.invalid_chain = self._generate_invalid_chain()
        self.blockchain = Blockchain(self.valid_chain)
        self.serialized = self.blockchain.serialize()

    def test_blockchain_string_representation(self):
        blockchain_str = str(self.blockchain)
        self.assertIn('Blockchain', blockchain_str)
        self.assertIn('Block', blockchain_str)
        self.assertTrue(all([f'index: {index}' in blockchain_str for index in range(self.chain_length)]))

    def test_blockchain_genesis_property(self):
        self.assertTrue(self.blockchain.genesis == self._get_genesis_block())

    @patch.object(Block, 'mine_block')
    def test_blockchain_last_block_property(self, mock_mine_block):
        last_block = self.blockchain.last_block
        new_block = self._generate_block(last_block)
        mock_mine_block.return_value = new_block
        self.assertTrue(last_block == self.blockchain.chain[-1])
        self.blockchain.add_block(new_block.data)
        self.assertFalse(last_block == self.blockchain.last_block)

    @patch.object(Block, 'mine_block')
    def test_blockchain_length_property(self, mock_mine_block):
        last_block = self.blockchain.last_block
        new_block = self._generate_block(last_block)
        mock_mine_block.return_value = new_block
        self.assertEqual(self.blockchain.length, self.chain_length)
        self.blockchain.add_block(new_block.data)
        self.assertNotEqual(self.blockchain.length, self.chain_length)

    def test_blockchain_serialize(self):
        self.assertIsInstance(self.serialized, list)
        self.assertTrue(all([isinstance(block, str) for block in self.serialized]))

    def test_blockchain_deserialize(self):
        deserialized = Blockchain.deserialize(self.serialized)
        self.assertIsInstance(deserialized, Blockchain)
        self.assertTrue(hasattr(deserialized, 'chain'))
        for block_one, block_two in zip(deserialized.chain, self.blockchain.chain):
            self.assertTrue(block_one == block_two)

    @patch.object(Blockchain, 'is_valid_schema')
    def test_blockchain_create_valid_schema(self, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        blockchain = Blockchain.create(self.valid_chain)
        self.assertTrue(mock_is_valid_schema.called)
        self.assertIsInstance(blockchain, Blockchain)
        self.assertEqual(blockchain.chain, self.valid_chain)

    @patch.object(Blockchain, 'is_valid_schema')
    def test_blockchain_create_invalid_schema(self, mock_is_valid_schema):
        err_message = '[Blockchain] Validation error.'
        mock_is_valid_schema.side_effect = Mock(side_effect=BlockchainError(err_message))
        with self.assertRaises(BlockchainError) as err:
            Blockchain.create(self.invalid_chain)
            self.assertTrue(mock_is_valid_schema.called)
            self.assertIsInstance(err, BlockchainError)
            self.assertIn(err_message, err.message)

    @patch.object(Block, 'mine_block')
    def test_add_block(self, mock_mine_block):
        last_block = self.blockchain.last_block
        new_block = self._generate_block(last_block)
        mock_mine_block.return_value = new_block
        self.blockchain.add_block(new_block.data)
        self.assertEqual(self.blockchain.length, self.chain_length + 1)
        self.assertFalse(self.blockchain.last_block == last_block)

    @patch.object(Blockchain, 'is_valid')
    def test_set_valid_chain_shorter_chain(self, mock_is_valid):
        mock_is_valid.return_value = True
        initial_length = self.blockchain.length
        short_chain = self.valid_chain.copy()
        short_chain.pop()
        self.blockchain.set_valid_chain(short_chain)
        self.assertFalse(mock_is_valid.called)
        self.assertTrue(len(short_chain) < self.blockchain.length)
        self.assertEqual(self.blockchain.length, initial_length)

    @patch.object(Blockchain, 'is_valid')
    def test_set_valid_chain_longer_chain(self, mock_is_valid):
        mock_is_valid.return_value = True
        longer_chain = self.valid_chain.copy()
        self.blockchain.chain.pop()
        initial_length = self.blockchain.length
        self.blockchain.set_valid_chain(longer_chain)
        self.assertTrue(mock_is_valid.called)
        self.assertTrue(initial_length < len(longer_chain))
        self.assertTrue(initial_length < self.blockchain.length)
        self.assertEqual(self.blockchain.length, len(longer_chain))

    def test_set_valid_chain_replace_chain(self):
        longer_chain = self.valid_chain.copy()
        self.blockchain.chain.pop()
        initial_length = self.blockchain.length
        self.blockchain.set_valid_chain(longer_chain)
        self.assertTrue(initial_length < len(longer_chain))
        self.assertTrue(initial_length < self.blockchain.length)
        self.assertEqual(self.blockchain.length, len(longer_chain))

    def test_set_valid_chain_invalid(self):
        initial_length = self.blockchain.length
        err_message = '[Blockchain] Validation error.'
        with self.assertRaises(AssertionError) as err:
            self.blockchain.set_valid_chain(self.invalid_chain)
            self.assertTrue(len(self.invalid_chain) > self.blockchain.length)
            self.assertTrue(self.blockchain.length, initial_length)
            self.assertIsInstance(err, AssertionError)
            self.assertIn(err_message, err.message)

    def test_blockchain_is_valid_schema_valid(self):
        Blockchain.is_valid(self.valid_chain)

    def test_blockchain_is_valid_schema_invalid(self):
        err_message = '[Blockchain] Validation error.'
        with self.assertRaises(BlockchainError) as err:
            Blockchain.is_valid(self.invalid_chain)
            self.assertIsInstance(err, BlockchainError)
            self.assertIn(err_message, err.message)

    def test_blockchain_is_valid_transaction_data(self):
        Blockchain.is_valid_transaction_data(self.blockchain.chain)

    def test_blockchain_is_valid_transaction_data_invalid_transaction(self):
        invalid_transaction = self._generate_transaction()
        invalid_transaction.input['signature'] = Wallet().sign(invalid_transaction.output)
        self.blockchain.add_block([invalid_transaction.info])
        err_message = 'Invalid transaction'
        with self.assertRaises(BlockchainError) as err:
            Blockchain.is_valid_transaction_data(self.blockchain.chain)
            self.assertIsInstance(err, BlockchainError)
            self.assertIn(err_message, err.message)

    def test_blockchain_is_valid_transaction_data_duplicate_transaction(self):
        transaction = self._generate_transaction()
        self.blockchain.add_block([transaction.info, transaction.info])
        err_message = 'Repetead transaction uuid found'
        with self.assertRaises(BlockchainError) as err:
            Blockchain.is_valid_transaction_data(self.blockchain.chain)
            self.assertIsInstance(err, BlockchainError)
            self.assertIn(err_message, err.message)

    def test_blockchain_is_valid_transaction_data_multiple_rewards(self):
        reward_transaction_1 = Transaction.reward_mining(Wallet())
        reward_transaction_2 = Transaction.reward_mining(Wallet())
        self.blockchain.add_block([reward_transaction_1.info, reward_transaction_2.info])
        err_message = 'Multiple mining rewards in the same block'
        with self.assertRaises(BlockchainError) as err:
            Blockchain.is_valid_transaction_data(self.blockchain.chain)
            self.assertIsInstance(err, BlockchainError)
            self.assertIn(err_message, err.message)

    def test_blockchain_is_valid_transaction_invalid_historic_balance(self):
        wallet = Wallet()
        invalid_transaction = self._generate_transaction(wallet)
        invalid_transaction.output[wallet.address] = 1000
        invalid_transaction.input['amount'] = 1001
        invalid_transaction.input['signature'] = wallet.sign(invalid_transaction.output)
        self.blockchain.add_block([invalid_transaction.info])
        err_message = 'historic balance inconsistency'
        with self.assertRaises(BlockchainError) as err:
            Blockchain.is_valid_transaction_data(self.blockchain.chain)
            self.assertIsInstance(err, BlockchainError)
            self.assertIn(err_message, err.message)
