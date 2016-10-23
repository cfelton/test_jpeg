
import myhdl
from myhdl import Signal, always_comb


def Signals(dtype, nitems):
    return [Signal(dtype) for _ in range(nitems)]


@myhdl.block
def assign(a, b):
    @always_comb
    def beh_assign():
        b.next = a

    return beh_assign
