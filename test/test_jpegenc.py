from __future__ import division
from __future__ import print_function

import sys
import os
import random
import datetime
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
    reset = ResetSignal(1, active=1, async=True)

    jpgv1 = JPEGEncV1(clock, reset, args=args)
    jpgv2 = JPEGEncV2(clock, reset, args=args)

    # prepare the cosimulation
    tbdut = prep_cosim(clock, reset, jpgv1, jpgv2, args=args)   

    # save the bitstreams here
    v1_bic,v2_bic = [None],[None]

    # clock generator (20 tick period)
    @always(delay(10))
    def tbclk():
        clock.next = not clock


    def _dump_bitstreams(v1_bic, v2_bic):
        """ dump the retrieved bitstreams
        """
        v1_non_zero = False
        for bb in v1_bic:
            if bb != 0:
                v1_non_zero = True
        
        print("V1 bitstream, len %d (more than zeros %s)" % (len(v1_bic),v1_non_zero,))
        for ii,bb in enumerate(v1_bic):
            print("  [%6d]  %08X" % (ii, int(bb),))
            if ii > 4 and not args.dump_bitstreams:
                break;

        print("V2 bitstream, len %d" % (len(v2_bic),))
        for ii,bb in enumerate(v2_bic):
            print("  [%6d]  %08X" % (ii, int(bb),))
            if ii > 4 and not args.dump_bitstreams:
                break


    def _test():
        # get the bus adapters to the encoders
        tbintf = (jpgv1.get_gens(), jpgv2.get_gens(),)
        finished = [Signal(bool(0)) for _ in range(2)]

        # open the image for testing
        img = Image.open(args.imgfn)

        def _pulse_reset():
            reset.next = reset.active
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
            
            for ii in range(100):
                yield clock.posedge
                
            if not args.no_wait:
                _dump_bitstreams(v1_bic[0], v2_bic[0], args)


            end_time = datetime.datetime.now()
            dt = end_time - args.start_time
            print("end simulation %s" % (dt,))
            raise StopSimulation
            
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # stimulate V1 (design1) 
        @instance
        def tbstimv1():
            yield delay(100)
            while reset == reset.active:
                yield delay(10)
            yield delay(100)
            yield clock.posedge

            # initialize the JPEG encoder            
            yield jpgv1.initialize()
            # send and image to be encoded
            yield jpgv1.put_image(img)

            # no_wait indicates to stream the input and exit,
            # don't wait the encoder to finish
            if args.no_wait:
                while not jpgv1.pxl_done:
                    yield delay(1000)
                    yield clock.posedge   
                    # this is a debug mode, after all pixles streamed
                    # in continue simulation for some period of time ...
                    for _ in range(600):
                        yield delay(1000)
            else:
                yield jpgv1.get_jpeg(v1_bic)
            
            finished[0].next = True

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # stimulate V2 (design2) 
        @instance
        def tbstimv2():  
            yield delay(100)
            while reset == reset.active:
                yield delay(10)          
            yield delay(100)
            yield clock.posedge

            yield jpgv2.put_image(img)

            # no_wait indicates to stream the input and exit,
            # don't wait the encoder to finish
            if args.no_wait:
                while not jpgv2.pxl_done:
                    yield delay(1000)
                    yield clock.posedge
                for _ in range(100):
                    yield delay(100)
            else:                
                yield jpgv2.get_jpeg(v2_bic)
            
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

    # randomly select a test image
    ipth = "./test_images/color/"
    ifn = 'small'
    while 'small' in ifn:
        ifn = random.choice(os.listdir(ipth))
    ipth = os.path.join(ipth, ifn)
    #ipth = os.path.join(ipth, 'small3.png')

    # setup arguments for the test (future capture from CLI)
    vmod = 'tb_jpegenc'
    args = Namespace(
        # tracing arguments
        trace=False,           # enable tracing (debug)
        vtrace=True,           # enable VCD tracing in Verilog cosim
        vtrace_level=0,        # Verilog VCD dumpvars level
        vtrace_module=vmod,    # Verilog VCD dumpvars module to trace

        imgfn=ipth,            # image to test compression

        # verification (debug) options
        build_only=False,      # compile the V* only, not test
        build_skip_v1=False,   # skip the V1 encoder compile
        nout=0,                # number of encoded outputs to capture (debug mode)
        no_wait=False,         # don't wait for the encoder, exit after input
        dump_bitstreams=False, # dump full bitstreams at the end
    )

    args.start_time = datetime.datetime.now()

    # run the JPEG encoder test
    print("Using image %s " % (ipth,))
    test_jpegenc(args)

