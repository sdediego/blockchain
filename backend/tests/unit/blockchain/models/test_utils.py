# encoding: utf-8

import random
import string
from unittest import TestCase
from unittest.mock import Mock, patch

from src.blockchain.models import utils
from src.config.settings import BLOCK_TIMESTAMP_LENGTH
from src.exceptions import BlockError


class BlockUtilsTest(TestCase):
    
    def setUp(self):
        super(BlockUtilsTest, self).setUp()
        self.arguments = ['test_index', 'test_timestamp', 'test_data', 'test_hash']
        self.hash = utils.hash_block(self.arguments)
    
    def test_get_utcnow_timestamp(self):
        timestamp = utils.get_utcnow_timestamp()
        self.assertIsInstance(timestamp, int)
        self.assertEqual(len(str(timestamp)), BLOCK_TIMESTAMP_LENGTH)

    def test_hash_block_same_unordered_inputs(self):
        test_hash = utils.hash_block(*self.arguments)
        test_hash_reverse = utils.hash_block(*reversed(self.arguments))
        self.assertEqual(test_hash, test_hash_reverse)
       
    def test_hash_block_different_inputs(self):
        test_hash = utils.hash_block(*self.arguments)
        item = random.choice(self.arguments)
        self.arguments.remove(item)
        test_hash_remove = utils.hash_block(*self.arguments)
        self.assertNotEqual(test_hash, test_hash_remove)
    
    @patch('src.blockchain.models.utils.json.dumps')
    def test_hash_block_stringify_error(self, mock_json_dumps):
        err_message = 'Could not encode block data to generate hash.'
        mock_json_dumps.side_effect = Mock(side_effect=BlockError(err_message))
        with self.assertRaises(BlockError) as err:
            utils.hash_block(*self.arguments)
            self.assertTrue(mock_json_dumps.called)
            self.assertIsInstance(err, BlockError)
            self.assertIn(err_message, err.message)

    def test_hex_to_binary_valid_hash(self):
        binary = utils.hex_to_binary(self.hash)
        self.assertIsInstance(binary, str)
        self.assertEqual(len(binary), 256)
        self.assertTrue(all([digit in ['0', '1'] for digit in binary]))

    def test_hex_to_binary_invalid_hash(self):
        item = random.choice(list(string.hexdigits[:16]))
        invalid_hash = self.hash.replace(item, 'x')
        err_message = 'invalid literal for int() with base 16'
        with self.assertRaises(Exception) as err:
            utils.hex_to_binary(invalid_hash)
            self.assertEqual(err.args[0], err_message)
