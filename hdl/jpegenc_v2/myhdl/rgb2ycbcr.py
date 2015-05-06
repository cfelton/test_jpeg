#!/bin/python
from myhdl import *
from random import randrange

Y1, Y2, Y3 = 4899, 9617, 1868
CB1, CB2, CB3 = -2764, -5428, 8192
CR1, CR2, CR3 = 8192, -6860, -1332
Y_OFFSET, CB_OFFSET, CR_OFFSET = 0, 2097152, 2097152

def rgb2ycbcr(y, cb, cr, r, g, b, clk, reset):
	""" A RGB to YCbCr converter with reset.

	I/O pins:
	--------
	y       : output 8-bit unsigned value in range of 0-255
	cb      : output 8-bit unsigned value in range of 0-255
	cr      : output 8-bit unsigned value in range of 0-255
	r 		: input 8-bit unsigned value in range of 0-255
	g 		: input 8-bit unsigned value in range of 0-255
	b 		: input 8-bit unsigned value in range of 0-255
	clk 	: input clock boolean signal
	reset	: input 8-bit boolean signal

	"""

	@always(clk.negedge, reset.posedge)
	def logic():
		if reset:
			YTemp = intbv(0)[22:]
			CbTemp = intbv(0)[22:]
			CrTemp = intbv(0)[22:]
			y.next = 0
			cb.next = 0
			cr.next = 0

		else:
			YTemp = intbv(Y_OFFSET + Y1 * r + Y2 * g + Y3 * b)[22:]
			CbTemp = intbv(CB_OFFSET + CB1 * r + CB2 * g + CB3 * b)[22:]
			CrTemp = intbv(CR_OFFSET + CR1 * r + CR2 * g + CR3 * b)[22:]

			y.next = YTemp[21:14] + 1 if YTemp[13] else YTemp[21:14]
			cb.next = CbTemp[21:14] + 1 if CbTemp[21:14] != 255 and CbTemp[13] else CbTemp[21:14]
			cr.next = CrTemp[21:14] + 1 if CrTemp[21:14] != 255 and CrTemp[13] else CrTemp[21:14]

	return logic

def test():
	y, cb, cr, r, g, b = [Signal(intbv(0)[8:]) for i in range(6)]

	clk, reset = Signal(bool(0)), Signal(bool(0))

	@always(delay(10))
	def clkgen():
		clk.next = not clk

	@always(clk.posedge)
	def stimulus():
		r.next = randrange(256)
		g.next = randrange(256)
		b.next = randrange(256)

		reset.next = True if (randrange(6) == 0) else False

	@instance
	def monitor():
		print "\t".join(['r', 'g', 'b', 'y', 'cb', 'cr', 'reset', 'clk', 'now'])
		print "-" * 70
		while True:
			yield delay(1)
			print "\t".join(["%d"]*9) % (r, g, b, y, cb, cr, reset, clk, now())
			yield delay(19)

	rgb2ycbcr_inst = rgb2ycbcr(y, cb, cr, r, g, b, clk, reset)

	sim = Simulation(clkgen, rgb2ycbcr_inst, stimulus, monitor)
	sim.run(500)

if __name__ == '__main__': test()
