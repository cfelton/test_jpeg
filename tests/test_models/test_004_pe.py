
import myhdl
from myhdl import instance, delay, StopSimulation
from rhea import Global, Clock

from jpegenc.models import DataStream
from jpegenc.models import ProcessingSubblock
from jpegenc.models.video import ColorBars
from jpegenc.models.video import BitstreamDevourer

from jpegenc.testing import run_testbench


def test_psb_basic():
    """Test a small chain of processing blocks with default config.
    """
    resolution = (1920, 1080)
    frame_rate = 60
    color_depth = (8, 8, 8)

    @myhdl.block
    def bench():
        clock = Clock(0, frequency=125e6)
        glbl = Global(clock)
        ck_drv = clock.gen()

        # a known generated video stream
        video_source = ColorBars(
            resolution=resolution, color_depth=color_depth,
            frame_rate=frame_rate
        )
        vd_proc = video_source.process(glbl)

        dw = len(video_source.pixel.data)
        pe_procs = []

        for ii in range(13):
            data_i = data_o if ii > 0 else video_source.pixel
            data_o = DataStream(data_width=dw)

            pe = ProcessingSubblock(cycles_to_process=24)
            pe_procs += [pe.process(glbl, data_i, data_o)]

        video_sink = BitstreamDevourer(video_source, encoder=None)
        vk_proc = video_sink.process(glbl, data_o)

        @instance
        def tbstim():
            while video_sink.num_data_words < 32:
                yield delay(1000)
            raise StopSimulation

        return myhdl.instances()

    run_testbench(bench, trace=True, bench_id="psb_basic")


def test_psb_buffered():
    pass


def test_psb_block():
    pass