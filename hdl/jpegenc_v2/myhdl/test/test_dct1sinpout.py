#!/bin/python
from myhdl import *
from dct1sinpout import *
from random import randrange

RANGE1_8 = range(8)

def print_list(signalList):
	for i in RANGE1_8:
		print "{:7d}".format(int(signalList[i])),
	print ""

def print_matrix(matrix):
	for i in RANGE1_8:
		print_list(matrix[i])

def test():
	output = [Signal(0) for _ in range(8)]
	input = Signal(0)
	enable_in, enable_out, clk, reset = [Signal(False) for _ in range(4)]

	@always(delay(10))
	def clkgen():
		clk.next = not clk

	@instance
	def stimulus():
		for i in RANGE1_8:
			yield clk.posedge
			input.next = 1
			enable_in.next = True

		# reset.next = True if (randrange(6) == 0) else False

	@instance
	def monitor():
		while True:
			yield delay(1)
			print "\t".join(['en_out', 'input', 'en_in', 'reset', ' clk', '  now'])
			print "\t".join(["  %d"]*6) % (enable_out, input, enable_in, reset, clk, now())
			print "-" * 72
			print_list(output)
			print "-" * 72
			yield delay(19)

	dct_inst = dct1SinPout(output, enable_out, input, enable_in, clk, reset)

	sim = Simulation(clkgen, dct_inst, stimulus, monitor)
	sim.run(20 * 8 + 1)

	# toVerilog(dct1SinPout, output, enable_out, input, enable_in, clk, reset)

if __name__ == '__main__': test()