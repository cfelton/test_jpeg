
import myhdl
from myhdl import ResetSignal, delay


@myhdl.block
def reset_on_start(reset, clock):
    assert isinstance(reset, ResetSignal)


@myhdl.block
def clock_driver(clock):
    pass


def pulse_reset(reset, clock):
    reset.next = reset.active
    yield delay(40)
    yield clock.posedge
    reset.next = not reset.active
    yield clock.posedge
