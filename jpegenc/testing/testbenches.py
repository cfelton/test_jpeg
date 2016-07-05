
import myhdl
from myhdl import SignalType, ResetSignal, delay, instance


@myhdl.block
def reset_on_start(reset, clock):
    assert isinstance(reset, ResetSignal)

    @instance
    def beh_reset():
        reset.next = reset.active
        yield delay(40)
        yield clock.posedge
        reset.next = not reset.active

    return beh_reset


@myhdl.block
def clock_driver(clock, period=10):
    d1 = period//2
    d2 = period-d1

    @instance
    def beh_clock():
        clock.next = True
        while True:
            yield delay(d1)
            clock.next = False
            yield delay(d2)
            clock.next = True

    return beh_clock


def toggle_signal(sig, clock):
    assert isinstance(sig, SignalType)
    assert not sig

    sig.next = True
    yield clock.posedge
    sig.next = False
    yield clock.posedge


def pulse_reset(reset, clock):
    reset.next = reset.active
    yield delay(40)
    yield clock.posedge
    reset.next = not reset.active
    yield clock.posedge
