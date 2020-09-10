# encoding: utf-8

from starlette.middleware.cors import CORSMiddleware as BaseCORSMiddleware

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
                                             allow_methods=["GET", "POST"], allow_headers=["*"])
