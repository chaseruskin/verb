#!/usr/bin/env bash

set -e

URL="https://github.com/cdotrus/verb"

pip install git+$URL.git@t"runk#egg=verb&subdirectory=src/lib/python"
orbit install verb --url $URL/archive/refs/heads/trunk.zip
cargo install --git $URL