#!/bin/bash
if [[ "$1" == "" ]]; then
    echo "Please provide the name of the key (filename)."
    exit -1
fi

ssh-keygen -t ed25519 -b 4096 -f "$1"