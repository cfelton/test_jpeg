from myhdl import block, delay, instance

class Pixel(object):
    def __init__(self):
        self.Y1 = 0
        self.Y2 = 1
        self.Cb = 2
        self.Cr = 3


@block
def tbclock(clock):
    @instance
    def clockgen():
        clock.next = False
        while True:
            yield delay(10)
            clock.next = not clock
    return clockgen

@block
def resetonstart(clock, reset):
    """reset block used for verification purpose"""
    @instance
    def reset_button():
        reset.next = True
        yield delay(40)
        yield clock.posedge
        reset.next = False
    return reset_button


def start_of_block(clock, start):
    start.next = True
    yield clock.posedge
    start.next = False
    yield clock.posedge


def reset_on_start(clock, reset):
    reset.next = True
    yield delay(40)
    yield clock.posedge
    reset.next = False
