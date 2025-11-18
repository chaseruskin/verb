import cocotb
from io import StringIO

def debug(*values: object, sep: str=' '):
    '''
    Logs the values with the DEBUG severity level.
    '''
    s = StringIO()
    print(*values, sep=sep, file=s, end='')
    cocotb.top._log.debug(s.getvalue())


def info(*values: object, sep: str=' '):
    '''
    Logs the values with the INFO severity level.
    '''
    s = StringIO()
    print(*values, sep=sep, file=s)
    cocotb.top._log.info(s.getvalue())


def warning(*values: object, sep: str=' '):
    '''
    Logs the values with the WARNING severity level.
    '''
    s = StringIO()
    print(*values, sep=sep, file=s)
    cocotb.top._log.warning(s.getvalue())


def error(*values: object, sep: str=' '):
    '''
    Logs the values with the ERROR severity level.
    '''
    s = StringIO()
    print(*values, sep=sep, file=s)
    cocotb.top._log.error(s.getvalue())


def critical(*values: object, sep: str=' '):
    '''
    Logs the values with the CRITICAL severity level.
    '''
    s = StringIO()
    print(*values, sep=sep, file=s)
    cocotb.top._log.critical(s.getvalue())
