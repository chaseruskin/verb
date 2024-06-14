# Project: Vertex
# File: justfile
#
# This file contains common commands for different stages in the development
# cycle.

# Perform an installation of the latest libraries using stable versions.
user-install:
    pip install git+"https://github.com/cdotrus/vertex.git@stable#egg=vertex"
    orbit install vertex:latest --url "https://github.com/cdotrus/vertex/archive/refs/heads/stable.zip"

# Perform an installation of the latest libraries using development versions.
dev-install:
    pip install -e src/lib/python --force
    orbit install --path src/lib/vhdl --force

# Checks to make sure all locations where a version is specified has the correct
# version.
version-ok VERSION:
    python scripts/version-ok.py {{VERSION}}

# Updates the agglomerated VHDL package.
agglo-vhdl:
    python scripts/agglomerate.py