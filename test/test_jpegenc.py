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

    jpgv1 = JPEGEncV1(clock, reset, args=args)
    jpgv2 = JPEGEncV2(clock, reset, args=args)

    tbdut = prep_cosim(clock, reset, jpgv1, jpgv2, args=args)    

    @always(delay(10))
    def tbclk():
        clock.next = not clock

    def _test():
        tbintf = (jpgv1.get_gens(), jpgv2.get_gens(),)
        finished = [Signal(bool(0)) for _ in range(2)]

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
            wait = True
            while wait:
                if False in finished:
                    yield delay(100)
                else:
                    wait = False
            
            for ii in range(1000):
                yield clock.posedge

            print("end simulation")
            raise StopSimulation
            
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # stimulate V1 (design1) 
        @instance
        def tbstimv1():
            yield delay(100)
            while reset == reset.active:
                yield delay(10)
            yield delay(100)
            yield clock.posedge

            # the V1 jpegenc needs to be configured.
            img = Image.open(args.imgfn)
            yield jpgv1.put_image(img)
            bic = [None]
            # @todo: wait for end of bitstream
            #yield jpgv1.get_jpeg(bic)
            
            while not jpgv1.done:
                yield delay(1000)
                yield clock.posedge            

            finished[0].next = True

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            
        # stimulate V2 (design2) 
        @instance
        def tbstimv2():  
            yield delay(100)
            while reset == reset.active:
                yield delay(10)          
            yield delay(100)
            yield clock.posedge

            img = Image.open(args.imgfn)
            yield jpgv2.put_image(img)
            bic = [None]
            yield jpgv2.get_jpeg(bic)
            
            while not jpgv2.done:
                yield delay(1000)
                yield clock.posedge

            finished[1].next = True

        return tbclk, tbstim, tbintf, tbstimv1, tbstimv2


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
        build_skip_v1=False
    )
    test_jpegenc(args)

