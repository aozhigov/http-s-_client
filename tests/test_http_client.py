import unittest
from pathlib import Path
from unittest.mock import patch

from http_client.__main__ import get_parser
from http_client.exceptions import ValueRequestTypeException, \
    HTTPSClientException, ConnectException, UnreadableFileException
from http_client.client import Client
from http_client.request import Request
from http_client.response import Response


class TestHttpClient(unittest.TestCase):

    def test_check_get_request(self):
        args = get_parser().parse_args(
            ['http://ptsv2.com/t/lp5td-1586273836/post'])
        req = Request(protocol=args.protocol,
                      method=args.request,
                      timeout=float(args.timeout),
                      data=args.data, url=args.url)
        assert ('GET /t/lp5td-1586273836/post HTTP/1.1\r\n' +
                'Host: ptsv2.com\r\n' +
                'Connection: close\r\n' +
                'Content-Length: 0\r\n\r\n') == str(req)

    def test_check_post_request_text(self):
        args = get_parser().parse_args(
            ['-d', 'Hello, World!',
             'http://ptsv2.com/t/lp5td-1586273836/post',
             '-x', 'POST'])
        temp = Request.prepare_data(data=args.data)
        req = Request(protocol=args.protocol,
                      method=args.request,
                      timeout=float(args.timeout),
                      data=temp, url=args.url)
        e = str(req)
        assert ('POST /t/lp5td-1586273836/post HTTP/1.1\r\n' +
                'Host: ptsv2.com\r\n' +
                'Connection: close\r\n' +
                'Content-Length: 13\r\n\r\n' +
                'Hello, World!') == e

    def test_bytes(self):
        args = get_parser().parse_args(
            ['-d', 'Hello',
             'http://ptsv2.com/t/lp5td-1586273836/post',
             '-x', 'POST',
             '-a', 'Mozilla/5.0',
             '-t', '3000',
             '-g', '10'])
        req = Request(protocol=args.protocol,
                      method=args.request,
                      timeout=float(args.timeout),
                      data=args.data, url=args.url,
                      agent=args.agent)
        e = str(req)
        b = bytes(req).decode('ISO-8859-1')
        assert b == e

    def test_check_post_request_from_file(self):
        path = Path.cwd() / 'tests' / 'resources' / 'test_text.txt'
        args = get_parser().parse_args(
            ['-f', str(path),
             'http://ptsv2.com/t/lp5td-1586273836/post',
             '-x', 'POST'])
        with path.open('w+') as f:
            f.write('abracadabra')
        assert 'abracadabra' == Request.prepare_data(data=args.file)

    def test_response(self):
        text = 'HTTP/1.1 200 Ok\r\n' \
               'Server: VK\r\n' \
               'Connection: close\r\n' \
               'Content-Type: text/html; charset=UTF-8\r\n\r\nHello'
        new_response = Response.from_bytes(
            text.encode('utf-8'), None)
        assert 200 == new_response.code
        assert ({'Server': 'VK',
                 'Connection': 'close',
                 'Content-Type': 'text/html; charset=UTF-8'} ==
                new_response.headers)
        assert 'UTF-8' == new_response.charset
        assert 'Hello' == new_response.message

    def test_prepare_headers(self):
        path = Path.cwd() / 'tests' / 'resources' / 'cookie.txt'
        args = get_parser().parse_args(
            ['http://ptsv2.com/t/lp5td-1586273836/post',
             '-H', 'Content-Length: 30',
             'Pory: tau',
             '-l', 'https://vk.com/',
             '-c', 'income=1',
             '-C', str(path),
             '-a', 'Chrome'])
        with path.open('w') as f:
            f.write('hello')

        req = Request(method=args.request,
                      agent=args.agent,
                      cookie_file=args.cookie_file,
                      cookie=args.cookie,
                      reference=args.reference,
                      headers=args.headers, url=args.url,
                      data=args.data)
        assert {'Content-Length': '30',
                'Pory': 'tau', 'Reference': 'https://vk.com/',
                'Cookie': 'hello', 'User-Agent': 'Chrome',
                'Host': 'ptsv2.com', 'Connection': 'close'} == req.headers

    @patch('http_client.client.Client')
    def test_request_http(self, mock_request):
        client_mock = mock_request()
        client_mock.do_request.return_value = \
            Response(message='Thank you for this dump. '
                             'I hope you have a lovely day!',
                     charset='', code=200, location='', protocol='',
                     headers=dict(), request=None)
        args = get_parser().parse_args(
            ['http://ptsv2.com/t/lp5td-1586273836/post'])
        req = Request(protocol=args.protocol,
                      method=args.request,
                      timeout=float(args.timeout),
                      data=args.data, url=args.url)
        data = client_mock.do_request(req)
        assert data is not None
        assert data.message == 'Thank you for this dump. ' \
                               'I hope you have a lovely day!'

    @patch('http_client.client.Client')
    def test_request_https(self, mock_request):
        client_mock = mock_request()
        client_mock.do_request.return_value = \
            Response(code=200,
                     message='<!DOCTYPE html>', charset='',
                     location='', protocol='', headers=dict(), request=None)
        args = get_parser().parse_args(
            ['https://habr.com/ru/'])
        req = Request(protocol=args.protocol,
                      method=args.request,
                      timeout=float(args.timeout),
                      data=args.data, url=args.url)
        data = client_mock.do_request(req)
        assert data is not None
        assert data.code == 200
        assert data.message.__contains__('<!DOCTYPE html>')

    def test_prepare_data(self):
        f = Request.prepare_data
        assert 'test' == f(data='test')
        assert f(data=None) == ''
        assert '' == f('')
        assert 'hello' == f('tests/resources/cookie.txt')

    def test_asserts(self):
        args = get_parser().parse_args(
            ['https://habr.com/ru/', '-x', 'HHHHEEE'])
        self.assertRaises(ValueRequestTypeException,
                          Request,
                          protocol=args.protocol,
                          method=args.request,
                          timeout=float(args.timeout),
                          data=args.data, url=args.url)
        args = get_parser().parse_args(
            ['https://habr.com/ru/', '-C', 'sdzc.txt'])
        self.assertRaises(HTTPSClientException,
                          Request,
                          protocol=args.protocol,
                          method=args.request,
                          timeout=float(args.timeout),
                          data=args.data, url=args.url,
                          cookie_file=args.cookie_file)
        args = get_parser().parse_args(
            ['httff://habrweerwd.erff/ru/'])
        client = Client()
        req = Request(protocol=args.protocol,
                      method=args.request,
                      timeout=float(args.timeout),
                      data=args.data, url=args.url)
        self.assertRaises(ConnectException, client.do_request, req)
        args = get_parser().parse_args(
            ['https://habr.com/ru/', '-f', str(Path.cwd())])
        self.assertRaises(UnreadableFileException,
                          Request,
                          protocol=args.protocol,
                          method=args.request,
                          timeout=float(args.timeout),
                          data=args.file, url=args.url,
                          cookie_file=args.cookie_file)

    @patch('http_client.client.Client')
    def test_redirect(self, mock_request):
        client_mock = mock_request()
        client_mock.do_request.return_value = \
            Response(message='<!DOCTYPE html>',
                     charset='', code=200, location='', protocol='',
                     headers=dict(), request=None)
        args = get_parser().parse_args(
            ['https://vk.com/feed'])
        req = Request(protocol=args.protocol,
                      method=args.request,
                      timeout=float(args.timeout),
                      data=args.data, url=args.url,
                      redirect=10)
        client = Client()
        data = client_mock.do_request(req)
        assert data is not None
        assert data.code == 200
        assert data.message.__contains__('<!DOCTYPE html>')

        req.redirect = 0
        self.assertRaises(ConnectException,
                          client.do_request, req)


if __name__ == '__main__':
    unittest.main()
