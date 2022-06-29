# Proxy for docker remote context containers

This application bind and listen local ports and proxy connections to remote docker host with associated docker containers

# Features

Connect to remote docker (wia context or manual `--host` / `env DOCKER_HOST`), getting containers with published tcp ports and proxy requests from localhost to remote docker host.

Supported OS:
- Macos
- Linux
- Windows (needed cli docker.exe, maybe downloaded from https://github.com/StefanScherer/docker-cli-builder/releases/latest)

# Using

## Run from binaries

1. [download latest binary](https://github.com/AMEST/remote-docker-context-proxy/releases/latest). Select for you OS
2. Set docker host:
   * Configure via cli: `docker context`
   * Configure via env variable: `export DOCKER_HOST="ssh://user@remote-docker"`
   * Run binary with args `--host "ssh://user@remote-docker"`
3. If needed listen privileged ports ( < 1024), add arg `--listen-system-ports`
4. If you want to interact via docker cli, add arg `--use-docker-cli` 
5. (Only for linux and macos) run `chmod +x` on binary `docker-remote-proxy-linux` / `docker-remote-proxy-macos`
6. Run binary:
   * Windows: `docker-remote-proxy.exe`
   * Linux: `./docker-remote-proxy-linux`
   * Macos: `./docker-remote-proxy-macos`

## Run from sources
1. Install python 3.8 (minimal version)
2. Install requirements (`pip install -r requirements.txt`)
3. Set docker host:
   * Configure via cli: `docker context`
   * Configure via env variable: `export DOCKER_HOST="ssh://user@remote-docker"`
   * Run with args `--host "ssh://user@remote-docker"`
4. If needed listen privileged ports ( < 1024), add arg `--listen-system-ports`
5. If you want to interact via docker cli, add arg `--use-docker-cli` 
6. Run: `python src/main.py`
