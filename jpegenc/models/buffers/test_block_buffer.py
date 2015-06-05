

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from myhdl import *

from _block_buffer import PixelStream
from _block_buffer import ImageBlock
from _block_buffer import mdl_block_buffer


def test_block_buffer():

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=False)
    pxl = PixelStream()
    bmem = ImageBlock(pxl, )

    def _test():
        pxl.clock = clock
        tbdut = mdl_block_buffer(pxl, bmem)
        tbpxl = pxl.generate_stream()

        @always(delay(5))
        def tbclk():
            clock.next = not clock

        @instance
        def tbstim():
            print("start simulation ...")
            reset.next = reset.active
            yield delay(33)
            reset.next = not reset.active
            yield delay(13)
            yield clock.posedge

            for ii in range(100):
                yield delay(100)
                yield clock.posedge

            print("end simulation ...")
            raise StopSimulation

        return tbdut, tbpxl, tbclk, tbstim


    g = traceSignals(_test)
    Simulation(g).run()


if __name__ == '__main__':
    test_block_buffer()