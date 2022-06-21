from socketserver import BaseRequestHandler, TCPServer
from socket import socket, AF_INET, SOCK_STREAM
import threading
import logging
from enum import Enum, auto


class ProxyType(Enum):
    TCP = auto()
    UDP = auto()


class TcpProxySockHandler(BaseRequestHandler):
    """
    Request Handler for the proxy server.
    Instantiated once time for each connection, and must
    override the handle() method for client communication.
    """

    PROXY_HOST = None
    PROXY_PORT = None
    Logger = logging.getLogger("TcpProxyHandler")

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024)
        self.Logger.info("Passing data from: {}".format(self.client_address[0]))

        # Create a socket to the localhost server
        sock = socket(AF_INET, SOCK_STREAM)
        # Try to connect to the server and send data
        try:
            sock.connect((self.PROXY_HOST, self.PROXY_PORT))
            sock.sendall(self.data)
            # Receive data from the server
            while 1:
                received = sock.recv(1024)
                if not received:
                    break
                # Send back received data
                self.request.sendall(received)
        finally:
            sock.close()


class ProxyServer():

    def __init__(self, proxy_host, proxy_port, type=ProxyType.TCP):
        if(type != ProxyType.TCP):
            raise NotImplementedError("Only TCP Proxy implemented")
        self.logger = logging.getLogger("ProxyServer")
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.type = type
        HOST = "127.0.0.1"

        class ThreadedTcpProxyHandler(TcpProxySockHandler):
            PROXY_HOST = proxy_host
            PROXY_PORT = proxy_port

        self.server = TCPServer((HOST, proxy_port), ThreadedTcpProxyHandler)
        self.ip, self.port = self.server.server_address
        self.logger.info("Creating %s proxy server with listen on %s and proxy to %s:%s", type, proxy_port, proxy_host, proxy_port)

    def start(self):
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()
        self.logger.info("Starting %s proxy to %s:%s", self.type, self.proxy_host, self.proxy_port)

    def stop(self):
        self.server.shutdown()
        self.logger.info("Stopping %s proxy to %s:%s", self.type, self.proxy_host, self.proxy_port)
