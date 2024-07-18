# Project: Verb
# File: justfile
#
# This file contains common commands for different stages in the development
# cycle.

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

_default:
	just --list

# A full end-to-end test from the /examples directory
test MOD *FLAGS:
    cd examples/{{MOD}}; orbit test --target gverb -- {{FLAGS}}

# Test the software library
test-sw-lib:
    python -m unittest src/lib/python/tests/*.py

# Test the hardware library
test-hw-lib:
    just agglo-vhdl
    cd src/lib/vhdl; orbit test --dut basic --target gverb

test-sw-bin:
    cd src/bin/verb; cargo test

# Perform an installation of the latest libraries using stable versions
user-install:
    just version-ok 0.1.0
    just agglo-vhdl
    pip install git+"https://github.com/cdotrus/verb.git@trunk#egg=verb"
    orbit install verb --url "https://github.com/cdotrus/verb/archive/refs/heads/trunk.zip"
    cargo install --git "https://github.com/cdotrus/verb.git"

# Perform an installation of the latest libraries using development versions
dev-install:
    just version-ok 0.1.0
    just agglo-vhdl
    pip install -e src/lib/python --force
    orbit install --path src/lib/vhdl --force
    cargo install --path src/bin/verb --force

dev-hw-install:
    just version-ok 0.1.0
    just agglo-vhdl
    orbit install --path src/lib/vhdl --force

# Checks to make sure all locations where a version is specified has the correct
# version
version-ok VERSION:
    python scripts/version-ok.py {{VERSION}}

# Updates the agglomerated VHDL package
agglo-vhdl:
    python scripts/agglomerate.py

# Run a simulation for "add" with Orbit and Verb running independent commands
ovg-add:
    cd examples/add; mkdir -p target/gsim
    cd examples/add; verb model -C target/gsim --dut "$(orbit get add --json)" --tb "$(orbit get add_tb --json)" --coverage "coverage.txt" add_tb.py
    cd examples/add; orbit t --target gsim --dut add --no-clean
    cd examples/add; verb check ./target/gsim/events.log --coverage ./target/gsim/coverage.txt --stats

# Run a simulation for "bcd" with Orbit and Verb running independent commands
ovg-bcd:
    cd examples/bcd; mkdir -p target/gsim
    cd examples/bcd; verb model -C target/gsim --dut "$(orbit get bcd_enc --json)" --tb "$(orbit get bcd_enc_tb --json)" --coverage "coverage.txt" bcd_enc_tb.py
    cd examples/bcd; orbit t --target gsim --no-clean
    cd examples/bcd; verb check ./target/gsim/events.log --coverage ./target/msim/coverage.txt --stats


# Download the latest relevant profile for Hyperspace Labs
config:
    git clone https://github.com/hyperspace-labs/orbit-profile.git "$(orbit env ORBIT_HOME)/profiles/hyperspace-labs"
    pip install -r "$(orbit env ORBIT_HOME)/profiles/hyperspace-labs/requirements.txt"
    orbit config --append include="profiles/hyperspace-labs/config.toml"
    curl https://sh.rustup.rs -sSf | sh -s -- -y
    install.sh

# Start a docker container
harbor:
    docker run -it -w $PWD --mount type=bind,src=$PWD,dst=$PWD --name fpga cdotrus/melodic-marimba:latest /bin/bash

# Remove the existing docker container
sail:
    docker container rm fpga