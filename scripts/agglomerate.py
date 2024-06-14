# Project: Vertex
# Script: agglomerate.py
#
# Reads the existing VHDL files and copies the existing functions and types 
# into a single combined package.

import os

PACKAGE_NAME = 'test'

SRC_DIR = './src/lib/vhdl/src'

FILE_ORDER = [
    ('events.vhd', True),
    ('tutils.vhd', True),
]

pkg_headers = []
pkg_bodies = []
 
for (path, should_inc) in FILE_ORDER:
    pkg_filepath = SRC_DIR + '/' + path
    
    if should_inc == False:
        print('info: excluding package ' + pkg_filepath + '...')
        continue
    
    print('info: copying package ' + pkg_filepath + '...')
    # read each file and locate its package header and body (if exists)
    with open(pkg_filepath, 'r') as fd:
        data = fd.read()
        KEY = '\npackage'
        i_header_start = data.lower().find(KEY)
        i_keep = data[i_header_start + len(KEY):].find('\n')
        i_header_end = data.lower().find('\nend package;')

        pkg_headers += [data[i_header_start + len(KEY) + i_keep:i_header_end]]

        KEY = '\npackage body'
        i_body_start = data.lower().find(KEY)
        # skip package body if it does not exist
        if i_body_start == -1:
            continue

        i_keep = data[i_body_start + len(KEY):].find('\n')
        i_body_end = data.lower().find('\nend package body;')

        pkg_bodies += [data[i_body_start + len(KEY) + i_keep:i_body_end]]
        pass
        pass
    pass


HEADER = '''\
-- Project: Vertex
-- Package: ''' + PACKAGE_NAME + '''
--
-- This package brings the separate VHDL packages under a single package
-- for more convenient importing. This package is auto-generated; DO NOT EDIT.

library ieee;
use ieee.std_logic_1164.all;

library std;
use std.textio.all;

library amp;
use amp.types.all;
use amp.cast.all;
'''

PACKAGE_DECL = 'package ' + PACKAGE_NAME + ' is'
for header in pkg_headers:
    PACKAGE_DECL += header[:-1]
PACKAGE_DECL += '\n\nend package;'

PACKAGE_BODY = 'package body ' + PACKAGE_NAME + ' is'
for body in pkg_bodies:
    PACKAGE_BODY += body
PACKAGE_BODY += '\n\nend package body;'

agglo_data = HEADER + '\n' + PACKAGE_DECL + '\n\n' + PACKAGE_BODY

agglo_filepath = SRC_DIR + '/' + PACKAGE_NAME + '.vhd'

rc = 0

if os.path.exists(agglo_filepath) == True:
    exiting_data = ''
    with open(agglo_filepath, 'r') as fd:
        exiting_data = fd.read()
    if exiting_data != agglo_data:
        print('info: agglomerated package is out of sync; rewriting file...')
        rc = 101
    else:
        print('info: agglomerated package is already up to date')
    pass

with open(agglo_filepath, 'w') as fd:
    fd.write(HEADER)
    fd.write('\n')
    fd.write(PACKAGE_DECL)
    fd.write('\n\n')
    fd.write(PACKAGE_BODY)
    pass

print('info: agglomerated package written to:', agglo_filepath)
exit(rc)