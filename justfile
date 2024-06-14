# Project: Vertex
# File: justfile
#
# This file contains common commands for different stages in the development
# cycle.

VERSION := "0.1.0"

# Perform an installation of the latest libraries using stable versions.
user-install:
    just version-ok
    just agglo-vhdl
    pip install git+"https://github.com/cdotrus/vertex.git@stable#egg=vertex"
    orbit install vertex:latest --url "https://github.com/cdotrus/vertex/archive/refs/heads/stable.zip"
    cargo install --path src/bin/vertex

# Perform an installation of the latest libraries using development versions.
dev-install:
    just version-ok
    just agglo-vhdl
    pip install -e src/lib/python --force
    orbit install --path src/lib/vhdl --force
    cargo install --path src/bin/vertex --force

# Checks to make sure all locations where a version is specified has the correct
# version.
version-ok:
    python scripts/version-ok.py {{VERSION}}

# Updates the agglomerated VHDL package.
agglo-vhdl:
    python scripts/agglomerate.py