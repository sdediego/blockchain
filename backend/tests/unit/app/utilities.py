# encoding: utf-8

import random

from tests.unit.logging import LoggingMixin


class NodesNetworkMixin(LoggingMixin):

    def _generate_uris(self, number: int):
        ports = set([self._get_random_port() for _ in range(number)])
        return [f'ws://127.0.0.1:{port}' for port in ports]

    def _get_random_port(self):
        return random.randint(4000, 5000)
