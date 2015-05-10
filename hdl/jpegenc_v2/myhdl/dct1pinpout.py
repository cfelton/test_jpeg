#!/bin/python
from myhdl import *
from dct1sinpout import MULT_MAT
def dct1PinPout(output, enable_out, input, enable_in, clk, reset):

	@instance
	def logic():
		count = modbv(0)[3:]
		while True:
			yield clk.negedge
			enable_out.next = False
			if reset:
				count = modbv(0)[3:]
			elif enable_in:
				for row in range(8):
					for index in range(8):
						output[index][row].next = output[index][row] + MULT_MAT[count][index] * input[row]
				if count == 7:
					for row in range(8):
						for index in range(8):
							if intbv(output[index][row].next)[17]:
								output[index][row].next = (output[index][row].next >> 18) + 1
							else:
								output[index][row].next = output[index][row].next >> 18
					enable_out.next = True
				count += 1

	return logic