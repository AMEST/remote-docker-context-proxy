import docker
import logging
import os
from urllib import parse

class DockerService(object):
    def __init__(self, docker_host = None):
        self.docker_host = docker_host
        self.docker_client = docker.DockerClient(base_url=docker_host, use_ssh_client=docker_host.startswith("ssh"))
        self.nodeInfo = self.docker_client.info()
        self.logger = logging.getLogger("DockerService")
    
    def getRemoteHost(self):
        return parse.urlparse(os.getenv("DOCKER_HOST") if self.docker_host == None else self.docker_host).hostname
    
    def getPublishedPorts(self):
        containers = self.docker_client.containers.list()
        ports = []
        for container in containers:
            for port in container.ports:
                if container.ports[port] == None:
                    continue
                publishedPort = container.ports[port][0]["HostPort"]
                ports.append({"internal":port, "published":int(publishedPort)})
        return ports
