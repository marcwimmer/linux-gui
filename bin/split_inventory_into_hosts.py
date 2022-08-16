#!/usr/bin/env python3
import sys
import pyaml
import yaml
from pathlib import Path

def str_presenter(dumper, data):
    try:
        dlen = len(data.splitlines())
        if (dlen > 1):
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    except TypeError as ex:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

inventory = Path(sys.argv[1])
content = yaml.load(inventory.read_text())
print(content)

hosts = {}
for key in content.keys():
    for host in content[key]['hosts']:
        hosts.setdefault(host, {})
        hosts[host][key] = {'hosts': host}
        hosts[host][key] = content[key]['hosts'][host]

for host in hosts:
    print("=================")
    print(host)
    print(hosts[host])
    file = inventory.parent / inventory.name.replace('.yml', f".{host}.yml")
    data = hosts[host]
    for key in data:
        value = data[key]
        data[key] = {'hosts': {}}
        data[key]['hosts'][host] = value

    nice = pyaml.dump(data)
    file.write_text(nice)

