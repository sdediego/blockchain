# encoding: utf-8

import random
from unittest import TestCase
from unittest.mock import patch

from src.blockchain.models.block import Block


class BlockMixin(TestCase):

    def _get_genesis_block(self):
        return Block.genesis()

    @patch.object(Block, '_is_valid_schema')
    def _generate_block(self, block: Block, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        testing_data = [random.randint(0, 100) for _ in range(10)]
        return Block.mine_block(block, testing_data)


class BlockchainMixin(BlockMixin):

    def _generate_valid_chain(self, length: int):
        chain = [self._get_genesis_block()]
        while len(chain) < length:
            last_block = chain[-1]
            chain.append(self._generate_block(last_block))
        return chain

    def _generate_invalid_chain(self):
        chain = self.valid_chain[:]
        block = self._generate_block(random.choice(chain[:-2]))
        block.index = chain[-1].index + 1
        chain.append(block)
        return chain
