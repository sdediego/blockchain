# encoding: utf-8

import uuid

from fastapi import Request as BaseRequest
from starlette.datastructures import Headers


class Request(BaseRequest):
    """
    Request with a unique X-Request-ID header.
    """

    def _set_request_id_header(self):
        request_id = uuid.uuid4().hex.encode('latin-1')
        self.scope['headers'].append((b'X-Request-ID', request_id))

    @property
    def headers(self) -> Headers:
        if not hasattr(self, '_headers'):
            self._set_request_id_header()
            self._headers = Headers(scope=self.scope)
        return self._headers
