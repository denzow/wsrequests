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
        self.latest_ws_url = None

    def __getattr__(self, attr_name):
        """
        Access for not defined attribute dispatch to requests.
        :param str attr_name:
        :return:
        """
        return getattr(self.http_client, attr_name)

    @property
    def is_valid_proxy(self):
        """
        :return:
        :rtype: bool
        """
        return all([
            self.proxy_url,
            self.proxy_port,
        ])

    def connect(self, ws_url):
        """
        connect websocket endpoint.
        :param str ws_url:
        """
        if self.ws:
            self.ws.close()
            self.logger.debug('disconnect websocket [{}]'.format(self.latest_ws_url))
            self.ws = None
        self.logger.debug('connect websocket [{}]'.format(ws_url))
        self.ws = self._get_ws_client(ws_url)

    def send_message(self, message):
        """
        send message via websocket to connected websocket server
        :param message:
        :return:
        """
        if not self.ws:
            raise WsRequestsError('Not WebSocket Connected.')
        self.logger.debug('send message [{}]'.format(message))
        self.ws.send(json.dumps(message))

    def receive_message(self):
        """
        receive message via websocket. if no message, wait for new message.
        :return:
        """
        message = self.ws.recv()
        self.logger.debug('receive message [{}]'.format(message))
        return json.loads(message)

    def _get_http_client(self):
        """
        get requests session instance
        :return:
        """
        client = requests.session()
        if self.is_valid_proxy:
            client.trust_env = False
            client.proxies.update({
                'http': self._get_proxy_url(),
                'https': self._get_proxy_url(),
            })
            for proxy in client.proxies:
                self.logger.debug('use proxy [{}]'.format(proxy))
        return client

    def _get_ws_client(self, ws_url):
        """
        get websocket client instance
        :param str ws_url:
        :return:
        """
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
        self.latest_ws_url = ws_url
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
        """
        requests.cookie translate to string. for websocket client.
        :return:
        """
        return ';'.join(['{}={}'.format(k, v) for k, v in self.http_client.cookies.items()])
