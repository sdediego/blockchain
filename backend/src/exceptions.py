# encoding: utf-8

class BaseError(Exception):
    """
    Handle generic exception.
    """

    def __init__(self, message: str = None, code: int = None):
        """
        Initialize BaseError class instance.

        :param str message: error description message.
        :param int code: error code number.
        :return BaseError: new class instance.
        """
        super(BaseError, self).__init__(message, code)
        if code is not None:
            self.code = code
            message = f'Error {self.code}. {message}'
        self.message = message


class BlockError(BaseError):
    """
    Handle exception for Block instances.
    """
    pass


class BlockchainError(BaseError):
    """
    Handle exception for Blockchain instances.
    """
    pass


class P2PServerError(BaseError):
    """
    Handle exception for P2PServer instances.
    """
    pass


class WalletError(BaseError):
    """
    Handle exception for Wallet instances.
    """
    pass
