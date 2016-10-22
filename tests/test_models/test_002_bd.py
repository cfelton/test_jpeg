
from random import randint

import myhdl
from myhdl import instance, delay, StopSimulation
from rhea import Global, Clock

from jpegenc.interfaces import DataStream
from jpegenc.models.video import BitstreamDevourer
from jpegenc.testing import run_testbench


def test_bitstream_devourer():

    clock = Clock(0, frequency=125e6)
    glbl = Global(clock)
    data = DataStream(data_width=24)
    video_sink = BitstreamDevourer(source=None, encoder=None)

    @myhdl.block
    def bench():
        ck_drv = clock.gen()
        vk_proc = video_sink.process(glbl, data)

        @instance
        def tbstim():
            npx = 23
            tcnt, timeout = 0, 4*npx
            vmax = data.data.max-1

            for _ in range(4):
                yield clock.posedge

            while video_sink.num_data_words < npx-1 and tcnt < timeout:
                data.valid.next = True
                data.data.next = randint(0, vmax)
                yield clock.posedge
                tcnt += 1
            data.valid.next = False
            yield clock.posedge
            yield delay(1000)

            nw = video_sink.num_data_words
            assert nw == npx, "{} != {}, in {} cycles".format(nw, npx, tcnt)
            raise StopSimulation

        return myhdl.instances()

    run_testbench(bench, trace=True, bench_id='devourbits')

