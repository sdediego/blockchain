#!/usr/bin/env python
# encoding: utf-8

import argparse
import asyncio
from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

import uvicorn

from src.app.api import app

# Custom logger for www module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


async def start_api_server(host: str, port: int):
    config = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(config)
    logger.info(f'[app] Blockchain API server running on port {port}')
    return await server.serve()


async def start_p2p_server(host: str, port: int):
    app.p2p_server.bind(host, port)
    logger.info(f'[app] Blockchain P2P server running on port {port}')
    return await app.p2p_server.start()


async def start_p2p_heartbeat(nodes: str):
    nodes = [node.strip() for node in nodes.split(',')] if nodes else []
    await app.p2p_server.connect_nodes(nodes)
    logger.info(f'[app] Blockchain P2P heartbeat up.')
    return await app.p2p_server.heartbeat()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Blockchain App')
    parser.add_argument('-ah', action='store', dest='api_host', default='127.0.0.1')
    parser.add_argument('-ap', action='store', dest='api_port', default=5000)
    parser.add_argument('-ph', action='store', dest='p2p_host', default='127.0.0.1')
    parser.add_argument('-pp', action='store', dest='p2p_port', default=6000)
    parser.add_argument('-n', action='store', dest='nodes', default='')
    args = parser.parse_args()

    process = asyncio.get_event_loop()
    servers = asyncio.gather(
        start_api_server(host=args.api_host, port=args.api_port),
        start_p2p_server(host=args.p2p_host, port=args.p2p_port),
        start_p2p_heartbeat(nodes=args.nodes))
    process.run_until_complete(servers)
