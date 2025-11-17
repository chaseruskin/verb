import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.handle import SimHandleBase

class Context:

    _now = None

    def __init__(self):
        # check to verify the previously called runner was cleaned up
        if Context._now is not None and Context.now().is_finished() == False:
            raise Exception('Test case not cleaned up properly')
        self.errors = 0
        self.asserts = 0
        self.clock = None
        self._finished = False
        # set the current controlled instance to be this newly created one
        Context._now = self

    @staticmethod
    def now():
        if Context._now is None:
            raise Exception('Test case not initialized properly')
        return Context._now
    
    def is_finished(self) -> bool:
        return self._finished
    
    def finish(self):
        self._finished = True
    
    def get_errors(self) -> int:
        return self.errors
    
    def get_asserts(self) -> int:
        return self.asserts
    
    def get_clock(self) -> Clock:
        return self.clock
    
    def inc_error(self):
        self.errors += 1

    def inc_asserts(self):
        self.asserts += 1

    def get_logger(self):
        return cocotb.top._log

    async def listen(self):
        try:
            while True:
                await wait(1_000_000)
        finally:
            if self.is_finished() == False:
                Context._now = None
                raise Exception('Test case not cleaned up properly')


def initialize(tb):
    from .coverage import Coverage
    runner = Context()
    Coverage.reset()
    runner.clock = Clock(tb.clk, 20, unit='ns')
    runner.clock.start(start_high=False)
    cocotb.start_soon(runner.listen(), name='verb')


def complete():
    runner = Context.now()
    runner.finish()
    errors = runner.get_errors()
    assertions = runner.get_asserts()
    error_word = 'error' if errors == 1 else 'errors'
    assert_word = 'assertion' if assertions == 1 else 'assertions'
    message = "Encountered "+str(errors)+" "+error_word+" (out of "+str(assertions)+" "+assert_word+")"
    assert errors == 0, message
    runner.get_logger().info("Passed "+str(assertions)+" "+assert_word)


def assert_eq(recv, expt):
    from .signal import Signal
    runner = Context.now()
    
    r_val = recv
    e_val = expt
    if isinstance(recv, SimHandleBase) or isinstance(recv, Signal):
        r_val = recv.value
    if isinstance(expt, SimHandleBase) or isinstance(expt, Signal):
        e_val = expt.value

    is_eq = r_val == e_val

    try:
        r_str = str(int(r_val))
    except:
        r_str = str(r_val)

    try:
        e_str = str(int(e_val))
    except:
        e_str = str(e_val)

    msg = ''
    if is_eq == True:
        msg = 'recevied '+r_str+' as expected'
    else:
        msg = 'received '+r_str+' but expects '+e_str
    
    logger = cocotb.top._log
    if isinstance(recv, Signal) and recv.get_handle() is not None:
        logger = recv.get_handle()._log
    if isinstance(recv, SimHandleBase):
        logger = recv._log

    runner.inc_asserts()
    if is_eq == True:
        logger.info(msg)
    else:
        logger.error(msg)
        runner.inc_error()


async def rising_edge(clk=None, cycles: int=1):
    if clk is None:
        clk = Context.now().get_clock().signal
    for _ in range(cycles):
        await RisingEdge(clk)


async def falling_edge(clk=None, cycles: int=1):
    if clk is None:
        clk = Context.now().get_clock().signal
    for _ in range(cycles):
        await FallingEdge(clk)


async def wait(time: float, unit: str='step'):
    await Timer(time=time, unit=unit)