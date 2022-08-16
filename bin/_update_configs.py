#!/usr/bin/env python3
from pathlib import Path
import configparser

"""

Write in playbook file dependencies like

#depends: ssh,b,c,d

"""

class Playbook(object):
    def __init__(self, filepath):
        self.filepath = Path(filepath)

    def __repr__(self):
        return f"{self.filepath.parent.name}"

    @property
    def depends(self):
        depends = list(filter(lambda x: x.strip().startswith("#depends:"), self.filepath.read_text().splitlines()))
        res = []
        for depend in depends:
            res += list(map(lambda x: x.strip(), depend.split(":")[1].strip().split(",")))
        return res

def _scan_roles():
    roles, playbooks = set(), []
    roles.add("./roles")

    base = Path(".")
    for path in sorted(base.rglob("roles/**/*")):
        if any(x.startswith(".") for x in path.parts):
            continue
        if (path / '.containsroles').exists():
            roles.add("./" + str(path.relative_to(base)))
        if not path.is_dir():
            if 'playbook' in path.name and path.name.endswith(".yml"):
                playbooks.append('./' + str(path.relative_to(base)))
    return list(sorted(roles)), playbooks

def _write_playbooks(playbooks, roles_paths):
    playbooks = list(map(lambda x: Playbook(x), playbooks))

    def dep(arg):
        '''
            Dependency resolver

        "arg" is a dependency dictionary in which
        the values are the dependencies of their respective keys.
        '''
        d=dict((k, set(arg[k])) for k in arg)
        r=[]
        while d:
            # values not in keys (items without dep)
            t=set(i for v in d.values() for i in v)-set(d.keys())
            # and keys without value (items without dep)
            t.update(k for k, v in d.items() if not v)
            # can be done right away
            r.append(t)
            # and cleaned up
            d=dict(((k, v-t) for k, v in d.items() if v))
        return r

    def resolve_with_playbook(depends):
        if not depends:
            return
        for depend in depends:
            depplaybook = [x for x in playbooks if x.filepath.parent.name == depend]
            if not depplaybook:
                raise Exception(f"Could not find dependency {depends}")
            if len(depplaybook) > 1:
                raise Exception(f"Too many dependencies found for {depends}")
            yield depplaybook[0]

    deps = dict((playbook, list(resolve_with_playbook(playbook.depends))) for playbook in playbooks)
    tree = dep(deps)
    flat = []
    for block in tree:
        for playbook in block:
            flat.append(playbook.filepath)

    content = "---\n"
    for playbook in sorted(flat):
        content += f"- import_playbook: {playbook}\n"
    Path("playbook.yml").write_text(content, encoding="utf-8")

def _update_config():
    path = Path("ansible.cfg")
    config = configparser.ConfigParser()
    config.read(str(path))
    roles_paths, playbooks = _scan_roles()
    config['defaults']['roles_path'] = ":".join(roles_paths)
    with open(path, 'w', encoding="utf-8") as file:
        config.write(file)

    _write_playbooks(playbooks, roles_paths)


if __name__ == "__main__":
    _update_config()
