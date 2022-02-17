#!/bin/bash

# Check if the script is running as root
# if [ "$(id -u)" != "0" ]; then
#    echo "This script must be run as root" 1>&2
#    exit 1
# fi

python3 exporter/main.py test.yaml
