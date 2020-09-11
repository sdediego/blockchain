# encoding: utf-8

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware as BaseCORSMiddleware

from src.app.request import Request
from src.config.settings import origins


class CORSMiddleware(BaseCORSMiddleware):
    """
    API Server middleware to implemente CORS specifications for 
    secure cross-domain access control.
    """

    def __init__(self):
        """
        Create a new CORSMiddleware instance.
        """
        super(CORSMiddleware, self).__init__(allow_origins=origins, allow_credentials=True,
                                             allow_methods=['GET', 'POST'], allow_headers=['*'])


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    API Server middleware to include a unique X-Request-ID
    in incoming requests headers.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        request = Request(request.scope, request.receive)
        return call_next(request)
