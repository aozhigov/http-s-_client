import sys
from argparse import ArgumentParser
from typing import List

from http_client.client import Client
from http_client.request import Request
from http_client.response import Response


def get_response(args, response: Response):
    if args.body_ignore:
        format_answer(response,
                      [f'HTTP/{response.protocol} '
                       f'{response.code} OK'], False)
    elif args.head_ignore:
        sys.stdout.write(response.message)
    elif args.verbose:
        format_answer(response, [f'{str(response.request)}\r\n',
                                 f'HTTP/{response.protocol} '
                                 f'{response.code} OK'])
    elif args.output:
        with open(args.output, 'bw+') as f:
            f.write(response.message
                    .encode(response.charset))
    else:
        format_answer(response, [f'HTTP/{response.protocol}'
                                 f' {response.code} OK'])


def format_answer(response: Response,
                  answer: List[str],
                  with_message=True):
    for header, value in response.headers.items():
        answer.append(f'{header}: {value}')

    if with_message:
        answer.append('\r\n' + response.message)

    sys.stdout.write('\r\n'.join(answer))


def get_parser():
    parser = ArgumentParser(description='HTTP(S) Client')
    group_data = parser.add_mutually_exclusive_group()
    group_data.add_argument('-d', '--data', type=str,
                            help='Set data for request', default='')
    group_data.add_argument('-f', '--file', type=str,
                            help='Set data from file')

    parser.add_argument('-x', '--request', type=str,
                        help='Set request method:'
                             'GET | POST | PUT | CONNECT | '
                             'PATCH | OPTIONS | DELETE | '
                             'HEAD | TRACE', default='GET')

    parser.add_argument('url', type=str,
                        help='Set URL (link to resource)')

    parser.add_argument('-l', '--reference', type=str,
                        help='Set previous URL')

    group_head_body = parser.add_argument_group()
    group_head_body.add_argument('-1', '--head_ignore', action='store_true',
                                 help='Ignore head of response')
    group_head_body.add_argument('-0', '--body_ignore', action='store_true',
                                 help='Ignore body of response')

    group_show = parser.add_mutually_exclusive_group()
    group_show.add_argument('-v', '--verbose', action='store_true',
                            help='Get detailed response (with request)')
    group_show.add_argument_group(group_head_body)

    parser.add_argument('-c', '--cookie', type=str,
                        help='Set cookie')

    parser.add_argument('-C', '--cookie_file', type=str,
                        help='Set cookie from file')

    parser.add_argument('-a', '--agent', type=str,
                        help='Set User Agent')

    parser.add_argument('-O', '--output', type=str,
                        help='Send answer in file')

    parser.add_argument('-H', '--headers', type=str, nargs='+',
                        help='Add headers in request')

    parser.add_argument('-t', '--timeout', type=float,
                        help='Set timeout(sec) for '
                             'connecting to the server',
                        default=1000)

    parser.add_argument('-p', '--protocol', type=str,
                        help='Set protocol', default='HTTP/1.1')

    parser.add_argument('-g', '--redirect', type=int,
                        help='Set max count redirect',
                        default=50)

    return parser


def main():
    args = get_parser().parse_args()

    request = Request(protocol=args.protocol,
                      timeout=args.timeout,
                      headers=args.headers,
                      method=args.request,
                      agent=args.agent,
                      cookie=args.cookie,
                      cookie_file=args.cookie_file,
                      reference=args.reference,
                      url=args.url,
                      data=args.data or args.file,
                      redirect=args.redirect)

    client = Client()
    response = client.do_request(request)
    get_response(args, response)


if __name__ == '__main__':
    main()
