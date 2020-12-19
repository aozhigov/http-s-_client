from enum import Enum

from http_client.exceptions import ValueRequestTypeException


class Method(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    CONNECT = 'CONNECT'
    TRACE = 'TRACE'

    @classmethod
    def check_request_type(cls, method: str):
        method = method.upper()
        try:
            return cls(method)
        except ValueError:
            raise ValueRequestTypeException(method)
