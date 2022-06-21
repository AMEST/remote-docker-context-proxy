# Proxy for docker remote context containers

This application bind and listen local ports and proxy connections to remote docker host with associated docker containers


# Using

1. Install python 3
2. Install requirements (`pip install -r requirements.txt`)
3. Set docker host. Example: `export DOCKER_HOST="ssh://user@remote-docker"`
4. Run: `python main.py`
