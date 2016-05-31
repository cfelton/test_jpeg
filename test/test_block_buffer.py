
from __future__ import print_function, division

import myhdl
from myhdl import Signal, ResetSignal, always, delay, instance, StopSimulation

from jpegenc.models.buffers import PixelStream, ImageBlock, mdl_block_buffer


def test_block_buffer():

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=False)
    pxl = PixelStream()
    bmem = ImageBlock(pxl, )

    def bench_block_buffers():
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

            for ii in range(200):
                yield delay(1000)
                yield clock.posedge

            print("end simulation ...")
            raise StopSimulation

        return tbdut, tbpxl, tbclk, tbstim


    g = myhdl.traceSignals(bench_block_buffers)
    myhdl.Simulation(g).run()


if __name__ == '__main__':
    test_block_buffer()