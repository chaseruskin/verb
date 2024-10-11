#!/usr/bin/env bash

set -e

URL="https://github.com/chaseruskin/verb"

pip install git+$URL.git@"trunk#egg=verb&subdirectory=src/lib/python"
orbit install verb --url $URL/archive/refs/heads/trunk.zip
cargo install --git $URL