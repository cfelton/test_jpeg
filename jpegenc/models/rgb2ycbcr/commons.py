#!/bin/python
from myhdl import *

ACTIVE_LOW, INACTIVE_HIGH = False, True
INACTIVE_LOW, ACTIVE_HIGH = False, True


def sintbv(value, nbits):
    nbits -= 1
    min_value = -1 << nbits
    max_value = -min_value + 1

    return intbv(value, min_value, max_value)


def round_signed(val, msb, lsb):
    if val[lsb - 1]:
        return val[msb:lsb].signed() + 1

    return val[msb:lsb].signed()


def round_unsigned(val, msb, lsb):
    temp=intbv(0)[msb:lsb]
    if val[lsb - 1]:
        temp[:]=val[msb:lsb] + 1
	return temp
    temp[:]=val[msb:lsb]
    return temp
