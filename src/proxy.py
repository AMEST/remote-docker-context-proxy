from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn
from socket import socket, AF_INET, SOCK_STREAM, gethostbyname, error
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

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.Logger.info("Passing data from: %s -> %s:%s" %(self.client_address[0], self.PROXY_HOST, self.PROXY_PORT))
        # Create a socket to the localhost server
        sock = socket(AF_INET, SOCK_STREAM)
        # Try to connect to the server and send data
        try:
            sock.connect((self.PROXY_HOST, self.PROXY_PORT))
            self.transferData(self.request, sock)
            # Receive data from the server
            self.Logger.info("Receive data: %s <- %s:%s" %(self.client_address[0], self.PROXY_HOST, self.PROXY_PORT))
            self.transferData(sock, self.request)
        finally:
            sock.close()

    def transferData(self, sock1 : socket, sock2 : socket, max_read_try = 10, receive_message_length = 2048):
        read_try = 0
        last_try = False
        sock1.setblocking(0)
        while True:
            try:
                msg = sock1.recv(receive_message_length)
                if not msg:
                    return
                sock2.sendall(msg)

                read_try = 0
                if last_try and len(msg) > 0:
                    last_try = False
                if len(msg) < (receive_message_length / 2):
                    if last_try:
                        return
                    else:
                        last_try = True
            except error as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    raise e
                if read_try > max_read_try:
                    return
                read_try += 1
                time.sleep(0.1)
                continue

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass
        
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
        self.server.shutdown()
        self.logger.info("Stopping %s proxy to %s:%s", self.type, self.proxy_host, self.proxy_port)
