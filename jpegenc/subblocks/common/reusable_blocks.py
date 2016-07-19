#!/usr/bin/env python
# coding=utf-8

from myhdl import Signal, intbv, block, always_comb

@block
def assign(a, b):
    """assign `a` to `b`

    a = b

    Arguments:
        a (SignalType): the signal to assign to
        b (SignalType): the signal to assign from

    myhdl convertible
    """
    @always_comb
    def assign():
            a.next = b

    return assign


@block
def assign_array(a, b):
    """assign one list-of-signals (`b`) to another (`a`)

    Arguments:
        a (list): list-of-signals to assign to (output)
        b (list): list-of-signals (input)

    myhdl convertible
    """
    assert isinstance(a, list)
    assert isinstance(b, list)
    assert len(a) == len(b)


    g = []
    for i in range(len(a)):
        g += [assign(a[i], b[i])]
    return g



