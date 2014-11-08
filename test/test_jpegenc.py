from __future__ import division
from __future__ import print_function

import sys
import os
import argparse
from argparse import Namespace

from PIL import Image
from myhdl import *

from _jpeg_prep_cosim import prep_cosim
# the interfaces to the encoders
from _jpeg_v1_intf import JPEGEncV1
from _jpeg_v2_intf import JPEGEncV2

def test_jpegenc(args):

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)
    jpegi = JPEGEncV2(clock, reset)

    tbdut = prep_cosim(clock, reset, jpegi, args=args)    

    @always(delay(10))
    def tbclk():
        clock.next = not clock

    def _test():
        tbintf = jpegi.get_gens()

        def _pulse_reset():
            yield delay(13)
            reset.next = reset.active
            yield delay(113)
            reset.next = not reset.active
            yield delay(13)
            yield clock.posedge

        @instance
        def tbstim():
            print("start simulation ...")
            yield _pulse_reset()
            
            img = Image.open(args.imgfn)
            yield jpegi.put_image(img)
            bic = [None]
            yield jpegi.get_jpeg(bic)
            
            while not jpegi.done:
                yield delay(1000)
                yield clock.posedge

            for ii in range(1000):
                yield clock.posedge

            print("end simulation")
            raise StopSimulation

        return tbclk, tbstim, tbintf


    if args.trace:
        traceSignals.name = 'vcd/_test_jpegenc'
        traceSignals.timescale = '1ns'    
        fn = traceSignals.name + '.vcd'
        if os.path.isfile(fn):
            os.remove(fn)
        gt = traceSignals(_test)
    else:
        gt = _test()

    # run the simulation
    Simulation((gt, tbdut,)).run()


if __name__ == '__main__':
    args = Namespace(
        trace=False,
        imgfn='smb.jpg',
        build_only=False,
        build_skip_v1=True
    )
    test_jpegenc(args)

