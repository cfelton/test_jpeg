#!/bin/python
from myhdl import *
from dct2sinpout import *
from random import randrange

RANGE1_8 = range(8)

def print_list(signalList):
	for i in RANGE1_8:
		print "{:6d}".format(int(signalList[i])),
	print ""

def print_matrix(matrix):
	for i in RANGE1_8:
		print_list(matrix[i])

da = [
	[154, 123, 123, 123, 123, 123, 123, 136],
	[192, 180, 136, 154, 154, 154, 136, 110],
	[254, 198, 154, 154, 180, 154, 123, 123],
	[239, 180, 136, 180, 180, 166, 123, 123],
	[180, 154, 136, 167, 166, 149, 136, 136],
	[128, 136, 123, 136, 154, 180, 198, 154],
	[123, 105, 110, 149, 136, 136, 180, 166],
	[110, 136, 123, 123, 123, 136, 154, 136]
]


def test():
	output = [[Signal(0) for x in range(8)] for x in range(8)]
	input = Signal(0)

	enable_out, enable_in, clk, reset = [Signal(False) for _ in range(4)]

	@always(delay(10))
	def clkgen():
		clk.next = not clk

	@instance
	def stimulus():
		for i in RANGE1_8:
			for j in RANGE1_8:
				yield clk.posedge
				input.next = da[i][j]
				enable_in.next = True

		# reset.next = True if (randrange(6) == 0) else False

	@instance
	def monitor():
		while True:
			yield delay(1)
			print "\t".join(['input', 'en_out', 'en_in', 'reset', 'clk', 'now'])
			print "\t".join(["%d"]*6) % (input, enable_out, enable_in, reset, clk, now())
			print "-" * 70
			print_matrix(output)
			print "-" * 70
			yield delay(19)

	dct_inst = dct2SinPout(output, enable_out, input, enable_in, clk, reset)

	sim = Simulation(clkgen, dct_inst, stimulus, monitor)
	sim.run(20 * (8 * 8 + 1) + 1)

if __name__ == '__main__': test()
