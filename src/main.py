from docker_service import DockerService
from proxy import ProxyType, ProxyServer
import subprocess
import json
import logging
import os
import time
import argparse

DOCKER_HOST_ENV = os.getenv("DOCKER_HOST")
ACTIVE_PROXIES = []
# Configure Logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=logging.DEBUG)

logging.getLogger("urllib3").setLevel(logging.INFO)
logging.getLogger("docker").setLevel(logging.INFO)

def getDockerHostFromContext():
    current_context_cmd = subprocess.run(["docker", "context", "inspect"], capture_output=True)
    current_context_json = json.loads(current_context_cmd.stdout.decode())
    return current_context_json[0]["Endpoints"]["docker"]["Host"]

def manageProxies(remote_docker_host_name, published_ports, listen_system_ports):
    global ACTIVE_PROXIES
    # Get only tcp services because only tcp proxy implemented
    published_ports = list(x["published"] for x in published_ports if x["internal"].endswith("tcp"))
    if not listen_system_ports:
        published_ports = list(x for x in published_ports if x > 1024)
    new_active_proxies = []
    # Add active proxy and stop inactive
    for proxy in ACTIVE_PROXIES:
        if(proxy.proxy_port in published_ports):
            new_active_proxies.append(proxy)
            published_ports.remove(proxy.proxy_port)
        else:
            proxy.stop()
    # Add and start new proxies
    for port in published_ports:
        proxy = ProxyServer(remote_docker_host_name, port, ProxyType.TCP)
        proxy.start()
        new_active_proxies.append(proxy)
    # Update proxy list
    ACTIVE_PROXIES = new_active_proxies

        

def mainLoop(docker_host, listen_system_ports, use_docker_cli):
    global ACTIVE_PROXIES
    logging.info("Initialize docker remote proxy to `%s`" %docker_host)
    docker_service = DockerService(docker_host, use_docker_cli)
    remote_docker_host_name = docker_service.getRemoteHost()
    
    try:
        while True:
            try:
                published_ports = docker_service.getPublishedPorts()
                manageProxies(remote_docker_host_name, published_ports, listen_system_ports)
            except Exception as e:
                logging.error(e)
            time.sleep(60)
    except KeyboardInterrupt:
        for proxy in ACTIVE_PROXIES:
            proxy.stop()
        logging.info('Docker remote proxy stopped!')
        return

if __name__ == "__main__":
    logging.info('Starting docker remote proxy!')
    parser = argparse.ArgumentParser(description='Remote docker context proxy')
    parser.add_argument('--listen-system-ports', action='store_true', help='Listen and Proxy system ports example: 22, 80, 443 etc.!')
    parser.add_argument('--use-docker-cli', action='store_true', help='Use docker cli instead of python docker client')
    parser.add_argument('--host', type=str, default=None, help='Docker host uri')
    args = parser.parse_args()
    if DOCKER_HOST_ENV != None:
        mainLoop(DOCKER_HOST_ENV, args.listen_system_ports, args.use_docker_cli)
    elif args.host != None:
        mainLoop(args.host, args.listen_system_ports, args.use_docker_cli)
    else:
        mainLoop(getDockerHostFromContext(), args.listen_system_ports, args.use_docker_cli)
