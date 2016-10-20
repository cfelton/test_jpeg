
import myhdl
from myhdl import instance, delay, StopSimulation
from rhea import Global, Clock

from jpegenc.models import DataStream
from jpegenc.models import ProcessingSubblock
from jpegenc.models.video import ColorBars
from jpegenc.models.video import BitstreamDevourer

from jpegenc.testing import run_testbench


def test_single_psb():
    """Test a single processing subblock

    This test will verify the basic building blocks to model and prototype
    the data flow through an image processing system.  The blocks uses
    are:
        ColorBars: video sources, generates the continuous video stream
        ProcessingSubblock: a generic model for a processing blocks
            (subblock) in the system.  In this test a single
    """
    resolution = (640, 480)
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

        # processing element that does nothing :)
        data = DataStream(data_width=len(video_source.pixel.data))
        pe = ProcessingSubblock(cycles_to_process=1)
        pe_proc = pe.process(glbl, video_source.pixel, data)

        # collect the output and compare if the video_source supports
        # checking, use an encoder (decode portion) if one exists
        video_sink = BitstreamDevourer(source=video_source, encoder=None)
        vk_proc = video_sink.process(glbl, data)

        @instance
        def tbstim():
            tcnt, timeout = 0, 10
            while video_sink.num_data_words < 5 and tcnt < timeout:
                yield delay(1000)
                tcnt += 1
            assert tcnt < timeout
            raise StopSimulation

        return myhdl.instances()

    run_testbench(bench, trace=True, bench_id="single_pe")

