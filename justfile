# Project: Verb
# File: justfile
#
# This file contains common commands for different stages in the development
# cycle.

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

_default:
	just --list

VERSION := "0.1.0"

# A full end-to-end test from the /examples directory
test MOD *FLAGS:
    cd examples/{{MOD}}; orbit test --target gverb -- {{FLAGS}}

pure:
    cd examples/add; mkdir -p target/gsim
    cd examples/add; verb model -C target/gsim --dut "$(orbit get add --json)" --tb "$(orbit get add_tb --json)" --coverage "coverage.txt" add_tb.py
    cd examples/add; orbit t --target gsim --dut add --dirty
    cd examples/add; verb check ./target/gsim/events.log --coverage ./target/gsim/coverage.txt --stats

pure2:
    cd examples/bcd; mkdir -p target/gsim
    cd examples/bcd; verb model -C target/gsim --dut "$(orbit get bcd_enc --json)" --tb "$(orbit get bcd_enc_tb --json)" --coverage "coverage.txt" bcd_enc_tb.py
    cd examples/bcd; orbit t --target gsim --dirty
    cd examples/bcd; verb check ./target/gsim/events.log --coverage ./target/gsim/coverage.txt --stats

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
    just version-ok
    just agglo-vhdl
    pip install git+"https://github.com/cdotrus/verb.git@trunk#egg=verb"
    orbit install verb --url "https://github.com/cdotrus/verb/archive/refs/heads/trunk.zip"
    cargo install --git "https://github.com/cdotrus/verb.git"

# Perform an installation of the latest libraries using development versions
dev-install:
    just version-ok
    just agglo-vhdl
    pip install -e src/lib/python --force
    orbit install --path src/lib/vhdl --force
    cargo install --path src/bin/verb --force

dev-hw-install:
    just version-ok
    just agglo-vhdl
    orbit install --path src/lib/vhdl --force

# Checks to make sure all locations where a version is specified has the correct
# version
version-ok:
    python scripts/version-ok.py {{VERSION}}

# Updates the agglomerated VHDL package
agglo-vhdl:
    python scripts/agglomerate.py