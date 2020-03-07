# encoding: utf-8

import random
import uuid

from src.blockchain.models.blockchain import Blockchain
from src.client.models.transaction import Transaction
from src.client.models.wallet import Wallet
from src.config.settings import MINING_REWARD, MINING_REWARD_INPUT
from tests.unit.logging import LoggingMixin


class ClientMixin(LoggingMixin):

    def setUp(self):
        self.wallet = Wallet()
        self.wallet.blockchain = self._generate_blockchain()
        self.recipient = Wallet.generate_address()
        self.amount = self._generate_float(ceil=self.wallet.balance)

    def _generate_blockchain(self, blocks : int = 5):
        blockchain = Blockchain()
        data = []
        for _ in range(0, blocks):
            transaction = self._generate_transaction()
            data.append(transaction.info)
        blockchain.add_block(data)
        return blockchain

    def _generate_transaction(self):
        output = {}
        output[self.wallet.address] = MINING_REWARD
        input = MINING_REWARD_INPUT
        id = uuid.uuid4().int
        return Transaction.create(uuid=id, input=input, output=output)

    def _generate_transactions_pool(self):
        pool = {}
        for _ in range(random.randint(1, 10)):
            transaction = self._generate_transaction()
            pool.update({transaction.uuid: transaction})
        return pool

    def _generate_float(self, floor: float = 0, ceil: float = 100):
        return random.uniform(floor, ceil)
