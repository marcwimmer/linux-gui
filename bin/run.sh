#!/bin/bash
base=`dirname $0`/..
cd "$base"
set -e

# export ANSIBLE_STRATEGY=debug

# sample
# bin/run.sh --limit '!humphrey' --limit '!hetzi1-direct' --limit 'all:!hetzi1-direct'

# TODO check if this works remotley
# bin/run.sh --limit '!hy-router-direct'

# only ovpn server:
#    --limit hy-router-direct

if [[ -z "$1" ]]; then
	echo "Pleaes provide a name!"
	exit -1
fi

if [[ ! -e "ansible.cfg" ]]; then
	cp bin/ansible.cfg.template ansible.cfg
fi

function allow_localhost_ssh_login () {
python3 <<EOF
from pathlib import Path
import os
import time
local_idrsa_pub = Path(os.path.expanduser("~/.ssh/id_rsa.pub"))
authorized_keys = Path(os.path.expanduser("~/.ssh/authorized_keys"))
if local_idrsa_pub.exists():
	key = local_idrsa_pub.read_text()
	if key not in (authorized_keys.exists() and authorized_keys.read_text() or ''):
		content = authorized_keys.read_text()
		content += "\n" + key + "\n"
		print("\n\n\nUpdating your ~/.ssh/authorized_keys file and adding your id_rsa key (needs ansible to execute actions).")
		print("Abort with ctrl+c otherwise just wait 10 seconds")
		time.sleep(5)
		authorized_keys.write_text(content)

EOF
}

allow_localhost_ssh_login
bin/_update_configs.py

if [[ -f "$HOME/.ssh/id_rsa.pub" ]]; then
	export PUBKEY="$(cat "$HOME/.ssh/id_rsa.pub")"
fi


ANSIBLE_ENABLE_TASK_DEBUGGER=True time ansible-playbook -i inventory/inventory.$1.yml "${@:2}" playbook.yml

if [[ "$?" != "0" ]]; then
	echo "Errors occurred for $1"
	exit -1
else
	exit 0
fi
