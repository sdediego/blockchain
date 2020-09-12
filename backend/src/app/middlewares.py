# encoding: utf-8

from logging import getLogger
from logging.config import fileConfig
from os.path import dirname, join

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.app.request import Request

# Custom logger for middlewares module
fileConfig(join(dirname(dirname(__file__)), 'config', 'logging.cfg'))
logger = getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    API Server middleware to include a unique X-Request-ID
    in incoming requests headers.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request = Request(request.scope, request.receive)
        return await call_next(request)


class RequestLogMiddleware(BaseHTTPMiddleware):
    """
    API Server middleware to log incoming requests and their
    response status.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        logger.info(f'[API] {request.method}. Request made to {request.url}.')
        response = await call_next(request)
        logger.info(f'[API] Response status {response.status_code}.')
        return response
