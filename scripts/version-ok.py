# Project: Vertex
# Script: version-ok.py
#
# Verifies all locations where a version is specified with an explicit value is
# the correct version.

import sys

version = sys.argv[1]

paths = [
    'src/lib/python/pyproject.toml',
    'src/bin/vertex/Cargo.toml',
    'src/lib/vhdl/Orbit.toml',
]


def load_lines(p: str):
    '''
    Retrieves the list of strings that are contained in the file at path `p`.
    '''
    lines = []
    with open(p, 'r') as fd:
        for l in fd.readlines():
            lines += [l[:-1]]
    return lines


def find_version_line(lines) -> str:
    '''
    Locates the line that specifies the version and returns it.
    '''
    data: str
    for data in lines:
        if data.startswith('version =') == True:
            return data
    else:
        print('error: failed to find version')
        exit(101)


def is_version_ok(current: str, line: str) -> bool:
    '''
    Checks to make sure the version is specified as the correct value as `current`.
    '''
    i = line.find('\"')
    j = line[i+1:].find('\"')
    got = line[i+1:i+1+j]
    return got == current


is_all_ok = True
for p in paths:
    is_ok = is_version_ok(version, find_version_line(load_lines(p)))
    print('info: is', version + '?' ' (' + str(is_ok).lower() + ')', str(p))
    if is_ok == False:
        is_all_ok = False
    pass


if is_all_ok == True:
    exit(0)
else:
    exit(101)
