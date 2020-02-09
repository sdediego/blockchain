# encoding: utf-8

import random

from src.client.models.wallet import Wallet
from tests.unit.logging import LoggingMixin


class ClientMixin(LoggingMixin):

    def setUp(self):
        self.wallet = Wallet()
        self.wallet.balance = self._generate_float()
        self.recipient = Wallet.generate_address()
        self.amount = self._generate_float(ceil=self.wallet.balance)

    def _generate_float(self, floor: float = 0, ceil: float = 100):
        return random.uniform(floor, ceil)
