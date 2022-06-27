import docker
import logging
import os
from urllib import parse
from docker_cli_wrapper import DockerCliWrappedContainer, DockerCLIWrapper

class DockerService(object):
    def __init__(self, docker_host = None, use_cli = False):
        self.docker_host = docker_host
        if use_cli or os.name == "nt":
            self.docker_client = DockerCLIWrapper()
            self.use_cli = True
        else:
            self.docker_client = docker.DockerClient(base_url=docker_host, use_ssh_client=True)
            self.use_cli = False
        self.nodeInfo = self.docker_client.info()
        self.logger = logging.getLogger("DockerService")
    
    def getRemoteHost(self):
        return parse.urlparse(os.getenv("DOCKER_HOST") if self.docker_host == None else self.docker_host).hostname
    
    def getPublishedPorts(self):
        containers = self.docker_client.containers.list() if not self.use_cli else self.docker_client.containers()
        ports = []
        for container in containers:
            if container.ports == None:
                continue
            for port in container.ports:
                if container.ports[port] == None:
                    ports.append({"internal":port, "published":int(port.replace("/tcp", "").replace("/udp", ""))})
                    continue
                publishedPort = container.ports[port][0]["HostPort"]
                ports.append({"internal":port, "published":int(publishedPort)})
        return ports
