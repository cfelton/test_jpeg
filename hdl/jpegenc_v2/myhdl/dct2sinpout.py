#!/bin/python
from myhdl import *
from dct1sinpout import dct1SinPout
from dct1pinpout import dct1PinPout

def dct2SinPout(output, enable_out, input, enable_in, clk, reset):
	enable_out_in = Signal(False)
	outin = [Signal(0) for _ in range(8)]

	dct1sinpout_inst = dct1SinPout(outin, enable_out_in, input, enable_in, clk, reset)
	dct1pinpout_inst = dct1PinPout(output, enable_out, outin, enable_out_in, clk, reset)

	return dct1sinpout_inst, dct1pinpout_inst
