#!/usr/bin/env python3
import click
from pathlib import Path
import subprocess
import os
import sys
import arrow

started = arrow.get()

errors = []

cmd = ["ansible-playbook"]
for inv in (Path(os.getcwd()) / 'inventory').glob("inventory.*"):
    cmd += [
        "-i",
        inv,
    ]
cmd += sys.argv[1:]
cmd += ['playbook.yml']

res = subprocess.check_call(cmd)
click.secho(f"Done: {inventory}", bold=True, fg='yellow')
click.secho(f"-------------------------------------------------------", fg='yellow')

click.secho(f"Took: {(arrow.get() - started).total_seconds()}", fg='green', bold=True)