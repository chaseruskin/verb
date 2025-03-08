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
    cd examples/{{MOD}}; orbit test -- {{FLAGS}}

# Test the software library
test-sw-lib:
    python -m unittest src/lib/python/tests/*.py

# No more bug!
bug:
    cd examples/sv/alu; mkdir -p target/vsim
    cd examples/sv/alu; verb model -C target/vsim --dut "$(orbit get alu --json)" --tb "$(orbit get alu_tb --json)" --coverage "coverage.txt" python -- ../../alu_tb.py

# Test the hardware library
test-hw-lib:
    just compile
    cd src/lib/vhdl; orbit test --dut basic --target gverb

test-sw-bin:
    cd src/bin/verb; cargo test

# Perform an installation of the latest libraries using stable versions
user-install:
    just version-ok 0.1.0
    just compile
    pip install git+"https://github.com/chaseruskin/verb.git@trunk#egg=verb"
    orbit install verb --url "https://github.com/chaseruskin/verb/archive/refs/heads/trunk.zip"
    cargo install --git "https://github.com/chaseruskin/verb.git"

# Perform an installation of the latest libraries using development versions
dev-install:
    just version-ok 0.1.0
    just compile
    pip install -e src/lib/python --force
    orbit install --path src/lib/vhdl --force --offline
    orbit install --path src/lib/systemverilog --force --offline
    export GIT_DESC_VERSION=$(git describe --tags)
    cargo install --path src/bin/verb --force

dev-hw-install:
    just version-ok 0.1.0
    just compile
    orbit install --path src/lib/hw --force

# Checks to make sure all locations where a version is specified has the correct
# version
version-ok VERSION:
    python scripts/version-ok.py {{VERSION}}

# Updates the agglomerated VHDL package
compile:
    python scripts/agglomerate.py

# Run a simulation for "add" with Orbit and Verb running independent commands
ovg-add:
    cd examples/vhdl/add; mkdir -p target/gsim
    cd examples/vhdl/add; verb model -C target/gsim --dut "$(orbit get add --json)" --tb "$(orbit get add_tb --json)" --coverage "coverage.txt" add_tb.py
    cd examples/vhdl/add; orbit t --target gsim --dut add --no-clean
    cd examples/vhdl/add; verb check ./target/gsim/events.log --coverage ./target/gsim/coverage.txt --stats

# Run a simulation for "bcd" with Orbit and Verb running independent commands
ovg-bcd:
    cd examples/vhdl/bcd; mkdir -p target/gsim
    cd examples/vhdl/bcd; verb model -C target/gsim --dut "$(orbit get bcd_enc --json)" --tb "$(orbit get bcd_enc_tb --json)" --coverage "coverage.txt" bcd_enc_tb.py
    cd examples/vhdl/bcd; orbit t --target gsim --no-clean
    cd examples/vhdl/bcd; verb check ./target/gsim/events.log --coverage ./target/gsim/coverage.txt --stats

# Run a simulation for "timer" with Orbit and Verb running independent commands
ovg-timer:
    cd examples/vhdl/timer; mkdir -p target/gsim
    cd examples/vhdl/timer; verb model -C target/gsim --dut "$(orbit get timer --json)" --tb "$(orbit get timer_tb --json)" --coverage "coverage.txt" timer_tb.py
    cd examples/vhdl/timer; orbit t --target gsim --no-clean
    cd examples/vhdl/timer; verb check ./target/gsim/events.log --coverage ./target/gsim/coverage.txt --stats

# Download the latest relevant profile for Hyperspace Labs
config:
    git clone https://github.com/chaseruskin/orbit-targets.git "$(orbit env ORBIT_HOME)/targets/chaseruskin"
    pip install -r "$(orbit env ORBIT_HOME)/targets/chaseruskin/requirements.txt"
    orbit config --append include="targets/chaseruskin/config.toml"
    curl https://sh.rustup.rs -sSf | sh -s -- -y
    install.sh

# Start a docker container
harbor:
    docker run -it -w $PWD --mount type=bind,src=$PWD,dst=$PWD --name fpga chaseruskin/melodic-marimba:latest /bin/bash

# Remove the existing docker container
sail:
    docker container rm fpga