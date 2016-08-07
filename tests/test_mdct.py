from __future__ import division, print_function

import sys
import os
from random import randint

import myhdl
from myhdl import (Signal, ResetSignal, intbv, always, delay, instance,
                   StopSimulation)

from jpegenc.testing import skip_ref_test
from support import get_cli_args


class DataBus(object):
    def __init__(self, w=8):
        self.data = Signal(intbv(0)[w:])
        self.dv = Signal(bool(0))


def prep_cosim(clock, reset, datai, datao, args=None):
    spth = '../hdl/jpegenc_v1/verilog'
    filelist = ['DCT1D.v', 'DCT2D.v', 'DBUFCTL.v', 
                'RAM.v', 'ROME.v', 'ROMO.v', 
                'MDCT.v']

    filelist = [os.path.join(spth, ff) for ff in filelist]
    filelist += ['tb_mdct.v']

    for ff in filelist:
        assert os.path.isfile(ff), "%s" % (ff,)

    cmd = "iverilog -g2001 -o mdct %s" % (" ".join(filelist))
    os.system(cmd)

    cmd = "vvp -m ./myhdl.vpi -lxt2 mdct"
    gcosim = myhdl.Cosimulation(cmd, 
                                clock=clock,
                                reset=reset,
                                dcti=datai.data,
                                idv=datai.dv,
                                dcto=datao.data,
                                odv=datao.dv)

    return gcosim


@skip_ref_test
def test_mdct(args=None):
    """ A simple test to exercise the MDCT block
    """

    clock = Signal(bool(0))
    reset = ResetSignal(1, active=1, async=True)
    
    datai = DataBus(w=8)
    datao = DataBus(w=12)
    fini = Signal(bool(0))

    tbdut = prep_cosim(clock, reset, datai, datao, args=args)

    @always(delay(10))
    def tbclk():
        clock.next = not clock

    def bench_mdct():
        numin_s  = Signal(0)
        numout_s = Signal(0)

        def pulse_reset():
            reset.next = reset.active
            yield delay(13)
            reset.next = reset.active
            yield delay(113)
            reset.next = not reset.active
            yield delay(13)
            yield clock.posedge

        @instance
        def tbmon():
            numin,numout = 0,0
            while True:
                yield clock.posedge
                if datao.dv:
                    numout += 1

                if datai.dv:
                    numin += 1
                
                if numin == (80*80*4)-1:
                    print("input finished")

                if numout == (80*80*4)-1:
                    print("output finished")
                    fini.next = True

                numin_s.next = numin
                numout_s.next = numout

        @instance
        def tbstim():
            yield pulse_reset()
            
            # @todo: use or remove
            # stream data in at max rate, 80x80x4 (4 components)
            # for row in range(80):
            #     for col in range(80):
            #         for cmp in range(4):
            #             datai.data.next = randint(0, 255)
            #             datai.dv.next = True
            #             yield clock.posedge

            # @todo: use or remove
            # stream data in at a slow rate (does all the output come out)
            # for ii in range(100):
            #     for jj in range(64):
            #         for cmp in range(4):
            #             datai.data.next = randint(0, 255)
            #             datai.dv.next = True
            #             yield clock.posedge
            #     datai.dv.next = False
            #     yield delay(2000)

            # only do 64 sample blocks 
            for ii in range(200):     # 400
                for nn in range(2):
                    for jj in range(64):  # 64
                        datai.data.next = randint(0, 255)
                        datai.dv.next = True
                        yield clock.posedge
                    # wait one clock
                    datai.dv.next = False
                    yield clock.posedge
                # wait a long time
                datai.dv.next = False
                yield delay(2000)

            # all done
            datai.dv.next = False
            yield clock.posedge

            # wait for all the outputs
            for ii in range(1000):
                yield delay(100)
                yield clock.posedge
                if fini: break

            yield delay(100)
            print(" %d in, %d out" % (numin_s, numout_s,))
            raise StopSimulation

        return tbclk, tbmon, tbstim

    gt = bench_mdct()
    myhdl.Simulation((gt, tbdut,)).run()
                        

if __name__ == '__main__':
    args = get_cli_args()
    test_mdct(args)
