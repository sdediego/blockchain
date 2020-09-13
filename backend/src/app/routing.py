# encoding: utf-8

from typing import Callable

from fastapi import APIRouter as BaseAPIRouter, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute as BaseAPIRoute

from src.app.p2p_server import P2PServer
from src.app.request import Request
from src.blockchain.models.blockchain import Blockchain
from src.client.models.transactions_pool import TransactionsPool
from src.client.models.wallet import Wallet


class APIRoute(BaseAPIRoute):
    """
    API Route for handling request validation errors.

    In case of unprocessable request a custom json response
    is sent back with error detail and 422 status code.
    """

    def get_route_handler(self) -> Callable:
        base_route_handler = super(APIRoute, self).get_route_handler()

        async def route_handler(request: Request) -> Response:
            try:
                return await base_route_handler(request)
            except RequestValidationError as err:
                body = await request.body()
                content = jsonable_encoder({'errors': err.errors(), 'body': body.decode()})
                return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return route_handler


class APIRouter(BaseAPIRouter):
    """
    Router to access common variables in multiple endpoints.
    """

    @property
    def blockchain(self) -> Blockchain:
        if not hasattr(self, '_blockchain'):
            self._blockchain = Blockchain()
        return self._blockchain

    @property
    def wallet(self) -> Wallet:
        if not hasattr(self, '_wallet'):
            self._wallet = Wallet(self.blockchain)
        return self._wallet

    @property
    def transactions_pool(self) -> TransactionsPool:
        if not hasattr(self, '_transactions_pool'):
            self._transactions_pool = TransactionsPool()
        return self._transactions_pool

    @property
    def p2p_server(self) -> P2PServer:
        if not hasattr(self, '_p2p_server'):
            self._p2p_server = P2PServer(self.blockchain, self.transactions_pool)
        return self._p2p_server
            