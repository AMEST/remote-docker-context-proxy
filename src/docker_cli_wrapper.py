import subprocess, json

class DockerCLIWrapper(object):
    def containers(self, all=False):
        ps_args = ['docker', 'ps', '--format', '"{{json .}}"', '--no-trunc']
        if all:
            ps_args.append('-a')
        ps = subprocess.run(ps_args, capture_output=True)
        ps_output_jsonl = ps.stdout.decode().split("\n")
        containers = []
        for container_json in ps_output_jsonl:
            containers.append(DockerCliWrappedContainer(container_json))
        
        return containers

    def info(self):
        info_args = ['docker', 'info', '--format', '"{{json .}}"']
        info = subprocess.run(info_args, capture_output=True)
        return json.loads(info.stdout.decode()[1:-2])


class DockerCliWrappedContainer(object):
    id = None
    image = None
    command = None
    createdAt = None
    labels = None
    names = None
    networks = None
    ports = None
    runningFor = None
    state = None
    status = None
    def __init__(self, jsonl):
        if len(jsonl) <= 2:
            return
        self.raw = json.loads(jsonl[1:-1])
        self.id = self.raw["ID"]
        self.image = self.raw["Image"]
        self.command = self.raw["Command"]
        self.createdAt = self.raw["CreatedAt"]
        self.labels = self.__parseLabels(self.raw["Labels"])
        self.ports = self.__parsePorts(self.raw["Ports"])
        self.networks = self.__parseNetworks(self.raw["Networks"])
        self.runningFor = self.raw["RunningFor"]
        self.state = self.raw["State"]
        self.status = self.raw["Status"]

    def __parseLabels(self, raw_json):
        labels = {}
        for label_str in raw_json.split(","):
            label = label_str.split("=")
            labels[label[0]] = label[1] if len(label) > 1 else ""
        return labels

    def __parsePorts(self, raw_json):
        if len(raw_json) == 0:
            return {}
        ports = {}
        for port_str in raw_json.split(", "):
            if port_str.find("->") == -1:
                ports[port_str] =[{"HostPort": port_str.replace("/tcp","").replace("/udp", "")}]
            else:
                port = port_str.replace("0.0.0.0:", "").split("->")
                ports[port[1]] = [{"HostPort":port[0]}]
        return ports

    def __parseNetworks(self, raw_json):
        if len(raw_json) == 0:
            return []
        return raw_json.split(",")