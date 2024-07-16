

class Log:

    _current = None

    def __init__(self, path: str):
        '''
        Loads a log file.
        '''
        self._events = []
        self._levels = dict()
        self._topics = dict()

        self._levels['ERROR'] = []
        self._levels['FATAL'] = []
        self._levels['WARNING'] = []

        with open(path, 'r') as fd:
            i = 0
            for e in fd.readlines():
                e = e.strip()
                (stamp, level, topic, subject, predicate) = e.split(maxsplit=4)
                self._events += [(stamp, level, topic, subject, predicate)]
                if level not in self._levels.keys():
                    self._levels[level] = []
                if topic not in self._topics.keys():
                    self._topics[topic] = []

                if topic.startswith('ASSERT'):
                    if 'ASSERT' not in self._topics.keys():
                        self._topics['ASSERT'] = []
                    self._topics['ASSERT'] += [i]
                    pass

                self._levels[level] += [i]
                self._topics[topic] += [i]
                i += 1
                pass
        pass

    pass


def current() -> Log:
    '''
    Accesses the current log associate with this context.
    '''
    from .context import Context
    if Log._current == None:
        Log._current = Log(Context.current()._context._event_log)
    return Log._current


def check() -> bool:
    log = current()
    errs = len(log._levels['ERROR']) + len(log._levels['FATAL'])
    return errs == 0


def summary() -> str:
    '''
    Returns a high-level overview of the event results.
    '''
    log = current()
    errs = len(log._levels['ERROR'])
    total = len(log._events)


    def count_okay(items) -> int:
        ok = 0
        for it in items:
            if log._events[it][1] == 'ERROR' or log._events[it][1] == 'FATAL':
                continue
            ok += 1
            pass
        return ok

    passed = count_okay(range(0, len(log._events)))
    total = len(log._events)
    print('Events:', str(passed) + '/' + str(total), '...'+str('OK') if passed == total else str('ERR'))
    for k, v in log._topics.items():
        if k.startswith('ASSERT_'):
            continue
        name = k[0].upper() + k[1:].lower()
        total = len(v)
        passed = count_okay(v)
        print(name + ':', str(passed) + '/' + str(total), '...'+str('OK') if passed == total else str('ERR'))
    return ''


def report_score() -> str:
    '''
    Formats the score as a `str`.
    '''
    log = current()
    asserts = log._topics['ASSERT']
    err_count = 0
    for i in asserts:
        if log._events[i] == 'ERROR' or log._events[i] == 'FATAL':
            err_count += 1
        pass
    assert_count = len(asserts)
    passed = assert_count - err_count
    total = assert_count
    percent = round((passed/total) * 100.0, 2) if total > 0 else None
    return (str(percent) + ' % ' if percent != None else 'N/A ') + '(' + str(passed) + '/' + str(total) + ' assertions)'

