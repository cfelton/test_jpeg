#!/bin/python
from myhdl import *
from dctconstructs import *
from dct1pinpout import *
from random import randrange

RANGE1_8 = range(8)

def print_list(signalList):
	for i in RANGE1_8:
		print "{:15d}".format(int(signalList[i])),
	print ""

def print_matrix(matrix):
	for i in RANGE1_8:
		print_list(matrix[i])


def test():
	output = [[Signal(0) for x in range(8)] for x in range(8)]
	input = PixelLine()

	enable_in, enable_out, clk = [Signal(INACTIVE_LOW) for _ in range(3)]
	reset = Signal(INACTIVE_HIGH)

	@always(delay(10))
	def clkgen():
		clk.next = not clk

	@instance
	def stimulus():
		for i in RANGE1_8:
			for j in RANGE1_8:
				if j == 0:
					input.pixels[j].next = i
				else:
					input.pixels[j].next = i
			enable_in.next = True
			yield clk.negedge

		# reset.next = True if (randrange(6) == 0) else False

	@instance
	def monitor():
		while True:
			yield delay(11)
			print "\t".join(['en_out', 'en_in', 'reset', 'clk', 'now'])
			print "\t".join(["%d"]*5) % (enable_out, enable_in, reset, clk, now())
			print "-" * 72
			print_list(input.pixels)
			print "-" * 70
			print_matrix(output)
			print "-" * 70
			yield delay(9)

	dct_inst = dct1PinPout(output, enable_out, input, enable_in, clk, reset)

	sim = Simulation(clkgen, dct_inst, stimulus, monitor)
	sim.run(20 * 8 + 1)

if __name__ == '__main__': test()
