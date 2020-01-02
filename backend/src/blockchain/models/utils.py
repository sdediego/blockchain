# encoding: utf-8

import hashlib
import json


def hash_block(*args):
    """
    Create a unique 256-bit hash value (64 characters length) from the rest
    of the block attributes values with sha256 cryptographic hash function.

    :param tuple args: sequence with all block attributes except hash.
    :return str: block unique hash attribute.
    """
    stringified = sorted(map(lambda arg: json.dumps(arg), args))
    joined = ''.join(stringified)
    return hashlib.sha256(joined.encode('utf-8')).hexdigest()
