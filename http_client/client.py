import io
import ssl
from socket import socket, AF_INET, SOCK_STREAM

from http_client.exceptions import ConnectException
from http_client.request import Request
from http_client.response import Response

CHUNK = 1024


class Client:
    @staticmethod
    def _get_response(sock, request: Request):
        response = bytearray()
        try:
            sock.connect((
                request.url.host,
                request.url.port))

            if request.url.scheme == 'https':
                sock.do_handshake()

            sock.sendall(bytes(request))

        except Exception:
            raise ConnectException(request.url.host + ': ' +
                                   str(request.url.port))

        while True:
            data = sock.recv(CHUNK)
            if not data or data == '':
                break
            response.extend(data)

        sock.close()

        return response

    def do_request(self, request: Request):
        response = Response.from_bytes(
            self._get_response(self._prepare_socket(request), request),
            request)

        if ((response.code == 302 or not response.location == '')
                and request.redirect > 0):
            temp_request = Request(url=response.location,
                                   reference=request.reference,
                                   cookie=request.cookie,
                                   agent=request.user_agent,
                                   headers=request.headers,
                                   method=request.request_method,
                                   cookie_file=request.cookie_file,
                                   timeout=request.timeout,
                                   redirect=request.redirect - 1,
                                   data=request.data,
                                   protocol=request.protocol)
            return self.do_request(temp_request)
        elif request.redirect == 0:
            raise ConnectException(str(request.url))

        return response

    @staticmethod
    def _prepare_socket(request: Request):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(request.timeout)

        if request.url.scheme == 'https':
            sock = ssl.wrap_socket(sock)

        return sock
