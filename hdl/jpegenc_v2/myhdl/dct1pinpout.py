#!/bin/python
from myhdl import *
from dctconstructs import *

def dct1PinPout(output, enable_out, input, enable_in, clk, reset):

	@instance
	def logic():
		count = modbv(0)[3:]
		temp = [[sintbv(0, 28) for _ in range(8)] for _ in range(8)]
		
		while True:
			yield clk.posedge, reset.negedge
			enable_out.next = INACTIVE_LOW
			if reset == ACTIVE_LOW:
				count = modbv(0)[3:]
				temp = [[sintbv(0, 28) for _ in range(8)] for _ in range(8)]
			elif enable_in == ACTIVE_HIGH:
				for row in range(8):
					for index in range(8):
						temp[index][row] += MULT_MAT[count][index] * input.pixels[row]

				if count == 7:
					for row in range(8):
						for index in range(8):
							output[index][row].next = round_signed(temp[index][row], 28, 18)

					enable_out.next = True
				count += 1

	return logic