import json

import requests
from websocket import create_connection

from logging import getLogger, Formatter, StreamHandler, DEBUG
default_logger = getLogger(__name__)
formatter = Formatter('%(asctime)s - %(levelname)s - %(threadName)s - %(message)s')
handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(formatter)
default_logger.setLevel(DEBUG)
default_logger.addHandler(handler)


class WsRequestsError(Exception):
    """ related errors"""


class WsRequests:

    def __init__(self, proxy_url=None, proxy_port=None, proxy_username=None, proxy_password=None, logger=None):

        self.proxy_url = proxy_url
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.logger = logger or default_logger

        self.http_client = self._get_http_client()
        self.ws = None

    def __getattr__(self, attr_name):
        return getattr(self.http_client, attr_name)

    @property
    def is_valid_proxy(self):
        return all([
            self.proxy_url,
            self.proxy_port,
        ])

    def connect(self, ws_url):
        if self.ws:
            self.ws.close()
        self.ws = self._get_ws_client(ws_url)

    def send_message(self, message):
        if not self.ws:
            raise WsRequestsError('Not WebSocket Connected.')

        self.ws.send(json.dumps(message))

    def receive_message(self):
        message = self.ws.recv()
        return json.loads(message)

    def _get_http_client(self):
        client = requests.session()

        if self.is_valid_proxy:
            client.trust_env = False
            client.proxies.update({
                'http': self._get_proxy_url(),
                'https': self._get_proxy_url(),
            })
        return client

    def _get_ws_client(self, ws_url):
        if self.is_valid_proxy:
            ws = create_connection(
                ws_url,
                cookie=self._get_session_cookie_string(),
                http_proxy_host=self.proxy_url,
                http_proxy_port=self.proxy_port,
                http_proxy_auth=(self.proxy_username, self.proxy_password)
            )
        else:
            ws = create_connection(
                ws_url,
                cookie=self._get_session_cookie_string(),
            )
        return ws

    def _get_proxy_url(self):
        if all([self.proxy_username, self.proxy_password]):
            return 'http://{username}:{password}@{host}:{port}/'.format(
                username=self.proxy_username,
                password=self.proxy_password,
                host=self.proxy_url,
                port=self.proxy_port
            )
        else:
            return 'http://{host}:{port}/'.format(
                host=self.proxy_url,
                port=self.proxy_port
            )

    def _get_session_cookie_string(self):
        return ';'.join(['{}={}'.format(k, v) for k, v in self.http_client.cookies.items()])

