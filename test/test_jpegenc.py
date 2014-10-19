from __future__ import division
from __future__ import print_function

import sys
import os
import argparse
from argparse import Namespace
from array import array

from myhdl import *

from _jpeg_prep_cosim import prep_cosim
from _jpeg_intf import JPEGEnc

def test_jpegenc(args):

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)
    jpegi = JPEGEnc()
    
    tbdut = prep_cosim(clock, reset, jpegi, args=args)

    @always(delay(10))
    def tbclk():
        clock.next = not clock

    def _test():
        
        @instance
        def tbstim():
            print("start simulation ...")
            yield delay(13)
            reset.next = reset.active
            yield delay(113)
            reset.next = not reset.active
            yield delay(13)
            yield clock.posedge

            for ii in xrange(100):
                yield clock.posedge

            print("end simulation")
            raise StopSimulation

        return tbclk, tbstim

    traceSignals.name = 'vcd/_test_jpegenc'
    traceSignals.timescale = '1ns'
    
    fn = traceSignals.name + '.vcd'
    if os.path.isfile(fn):
        os.remove(fn)

    Simulation((traceSignals(_test), tbdut,)).run()

if __name__ == '__main__':
    args = Namespace()
    test_jpegenc(args)

