#!/usr/bin/env python
# coding=utf-8

from myhdl import Signal, intbv, block, always_comb

@block
def assign(a, b):

    @always_comb
    def assign():
            a.next = b

    return assign


@block
def assign_array(a, b):

    assert isinstance(a, list)
    assert isinstance(b, list)
    assert len(a) == len(b)


    g = []
    for i in range(len(a)):
        g += [assign(a[i], b[i])]
    return g



