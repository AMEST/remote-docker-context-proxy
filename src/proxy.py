from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, error, timeout
import threading
import logging
from enum import Enum, auto
import errno
import time

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
    CONNECTION_ACTIVE = True

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.Logger.info("Passing data from: %s -> %s:%s" %(self.client_address[0], self.PROXY_HOST, self.PROXY_PORT))
        # Create a socket to the localhost server
        sock = socket(AF_INET, SOCK_STREAM)
        # Try to connect to the server and send data
        try:
            sock.connect((self.PROXY_HOST, self.PROXY_PORT))

            requestThread = threading.Thread(target=self.transfer_data, args=(self.request, sock))
            requestThread.daemon = True
            requestThread.start()

            self.transfer_data(sock, self.request)

        finally:
            sock.close()
            self.CONNECTION_ACTIVE = False
            self.Logger.info("Connection %s -> %s:%s closed" %(self.client_address[0], self.PROXY_HOST, self.PROXY_PORT))

    def transfer_data(self, sock1 : socket, sock2 : socket, receive_message_length = 2048):
        #setup socket receive timeout
        sock1.settimeout(5.0)
        while True:
            try:
                if not self.CONNECTION_ACTIVE or self.server.SHUTDOWN_REQUESTED:
                    return
                msg = sock1.recv(receive_message_length)
                if not msg:
                    break
                sock2.sendall(msg)
            except timeout:
                pass
        self.CONNECTION_ACTIVE = False

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    SHUTDOWN_REQUESTED = False
        
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
            PROXY_HOST = gethostbyname(proxy_host)
            PROXY_PORT = proxy_port

        self.server = ThreadedTCPServer((HOST, proxy_port), ThreadedTcpProxyHandler)
        self.ip, self.port = self.server.server_address
        self.logger.info("Creating %s proxy server with listen on %s and proxy to %s:%s", type, proxy_port, proxy_host, proxy_port)

    def start(self):
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()
        self.logger.info("Starting %s proxy to %s:%s", self.type, self.proxy_host, self.proxy_port)

    def stop(self):
        self.server.SHUTDOWN_REQUESTED = True
        self.server.shutdown()
        self.logger.info("Stopping %s proxy to %s:%s", self.type, self.proxy_host, self.proxy_port)
