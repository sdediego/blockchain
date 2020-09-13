#!/usr/bin/env python
# encoding: utf-8

import argparse
import asyncio
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

import uvicorn
from argparse import Namespace
from fastapi import FastAPI

from src.app.api import app

# Custom logger for www module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class BlockchainApp(object):
    """
    Blockchain application controller. 
    """

    def __init__(self, app: FastAPI, args: Namespace):
        """
        Create a new BlockchainApp instance.

        :param FastAPI app: blockchain application backend API.
        :param Namespace args: command line arguments.
        """
        nodes = [node.strip() for node in args.nodes.split(',')] if args.nodes else []
        self.app = app
        self.app.host = args.api_host
        self.app.port = args.api_port
        self.app.router.p2p_server.bind(args.p2p_host, args.p2p_port)
        self.app.router.p2p_server.add_uris(nodes)

    async def start_api_server(self):
        """
        Start blockchain application backend API server.
        """
        config = uvicorn.Config(self.app, host=self.app.host, port=self.app.port)
        server = uvicorn.Server(config)
        logger.info(f'[BlockchainApp] Blockchain API server running on port {self.app.port}.')
        await server.serve()

    async def start_p2p_server(self):
        """
        Start blockchain application backend peer-to-peer socket server.

        :return WebSocketServer: Blockchain backend peer-to-peer server.
        """
        logger.info(f'[BlockchainApp] Blockchain P2P server running on port {self.app.router.p2p_server.port}.')
        return await self.app.router.p2p_server.start()

    async def start_p2p_heartbeat(self):
        """
        Start blockchain application backend peer-to-peer server beat.
        """
        logger.info(f'[BlockchainApp] Blockchain P2P server heartbeat up.')
        await self.app.router.p2p_server.connect_nodes()
        await self.app.router.p2p_server.heartbeat()

    def run(self):
        """
        Start infinite loop to run all servers asynchronously in the same thread.
        """
        process = asyncio.get_event_loop()
        servers = asyncio.gather(self.start_api_server(), self.start_p2p_server(), self.start_p2p_heartbeat())
        process.run_until_complete(servers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='BlockchainApp')
    parser.add_argument('-ah', action='store', dest='api_host', default='127.0.0.1')
    parser.add_argument('-ap', action='store', dest='api_port', default=5000)
    parser.add_argument('-ph', action='store', dest='p2p_host', default='127.0.0.1')
    parser.add_argument('-pp', action='store', dest='p2p_port', default=6000)
    parser.add_argument('-n', action='store', dest='nodes', default='')
    args = parser.parse_args()

    blockchain_app = BlockchainApp(app, args)
    blockchain_app.run()
