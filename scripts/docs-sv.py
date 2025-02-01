# Extract the documentation for the SystemVerilog package and generate
# its corresponding API markdown file.

# Hard-coded path to the SV package
SOURCE = 'src/lib/hdl/src/godan.sv'

DEST = 'docs/src/reference/api-systemverilog.md'

REPOSITORY = 'https://github.com/chaseruskin/verb/blob/trunk'

def detect_item(ptr: int, lines) -> bool:
    '''
    Detect a line that requires documentation.
    '''
    l: str = lines[ptr].strip()
    return l.startswith('function') or \
        l.startswith('task') or \
        l.startswith('typedef')


def extract_docs(ptr: int, lines):
    docs = []
    ptr = ptr-1
    l = lines[ptr].strip()
    while l.startswith('//'):
        docs.insert(0, l.strip().strip('//').strip())
        ptr = ptr - 1
        l = lines[ptr].strip()
        pass
    return docs


def write_docs(key, val) -> str:
    result = ''
    result += '`[Verilog] '+key+'`\n\n'
    for v in val:
        result += v
    result += '\n\n<br>\n\n'
    return result


def main():

    funcs = dict()
    tasks = dict()
    types = dict()

    package = None

    # Extract the relevant documentation
    with open(SOURCE, 'r') as fd:
        lines = fd.readlines()
        for i in range(0, len(lines)):
            if lines[i].strip().startswith('package'):
                package = str(lines[i].strip().split(' ')[1].strip(';'))
            if detect_item(i, lines):
                item = lines[i].strip().strip(';')
                docs = extract_docs(i, lines)
                if item.startswith('function'):
                    funcs[item] = docs
                elif item.startswith('task'):
                    tasks[item] = docs
                elif item.startswith('typedef'):
                    types[item] = docs
        pass

    # Generate the markdown docs
    with open(DEST, 'w') as fd:
        fd.write('# SystemVerilog API\n\n')
        fd.write('Reference documentation for the Verb conjugations in SystemVerilog.\n\n')
        fd.write('## Package `'+package+'`\n[source]('+REPOSITORY+'/'+SOURCE+')\n\n')
        fd.write('### Typedefs\n')
        for key, val in types.items():
            fd.write(write_docs(key, val))
        fd.write('### Functions\n')
        for key, val in funcs.items():
            fd.write(write_docs(key, val))
        fd.write('### Tasks\n')
        for key, val in tasks.items():
            fd.write(write_docs(key, val))

    pass


if __name__ == "__main__":
    main()