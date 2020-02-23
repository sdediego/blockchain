# encoding: utf-8

import random
import uuid
from unittest.mock import patch

from src.blockchain.models.block import Block
from src.client.models.transaction import Transaction
from src.client.models.wallet import Wallet
from tests.unit.logging import LoggingMixin


class BlockMixin(LoggingMixin):

    def _get_genesis_block(self):
        return Block.genesis()

    @patch.object(Block, 'is_valid_schema')
    def _generate_block(self, block: Block, mock_is_valid_schema):
        mock_is_valid_schema.return_value = True
        transaction = self._generate_transaction()
        data = [transaction.info]
        return Block.mine_block(block, data)

    def _generate_transaction(self, sender: Wallet = None):
        recipient = uuid.uuid4().hex
        amount = random.randint(0, 100)
        sender = sender or Wallet()
        transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
        return transaction


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
