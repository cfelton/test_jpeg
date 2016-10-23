
import myhdl
from myhdl import instance, delay, StopSimulation
from rhea import Global, Clock

from jpegenc.interfaces import DataStream
from jpegenc.models import ProcessingSubblock
from jpegenc.models.video import ColorBars
from jpegenc.models.video import BitstreamDevourer

from jpegenc.testing import run_testbench

# global parameters for the tests
RESOLUTION = (1920, 1080)
COLOR_DEPTH = (8, 8, 8)
FRAME_RATE = 60
CLOCK_FREQUENCY = 125e6


def test_single_psb():
    """Test a single processing subblock

    This test will verify the basic building blocks to model and prototype
    the data flow through an image processing system.  The blocks uses
    are:
        ColorBars: video sources, generates the continuous video stream
        ProcessingSubblock: a generic model for a processing blocks
            (subblock) in the system.  In this test a single
    """

    @myhdl.block
    def bench():
        clock = Clock(0, frequency=CLOCK_FREQUENCY)
        glbl = Global(clock)
        ck_drv = clock.gen()

        # a known generated video stream
        video_source = ColorBars(
            resolution=RESOLUTION, color_depth=COLOR_DEPTH,
            frame_rate=FRAME_RATE
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


def test_psb_chain():
    """Test a small chain of processing blocks with default config.
    This test verifies that psb can be chained together and that
    some data will be passed to the sink.
    """
    num_pe = 31

    @myhdl.block
    def bench():
        clock = Clock(0, frequency=CLOCK_FREQUENCY)
        glbl = Global(clock)
        ck_drv = clock.gen()

        # a known generated video stream
        video_source = ColorBars(
            resolution=RESOLUTION, color_depth=COLOR_DEPTH,
            frame_rate=FRAME_RATE
        )
        vd_proc = video_source.process(glbl)

        dw = len(video_source.pixel.data)
        pe_procs, data_o = [], None

        for ii in range(num_pe):
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


def test_psb_cycles():
    """Test the cycles to process.
    Test the generic ProcessingSubblock cycles to process, a data in
    should not be available out until the number of clock cycles has
    pass.  Verify the data generated is captured in the sink.
    """
    pass


def test_psb_buffered():
    """Test the buffers
    Test the buffered inputs and outputs.  The model the buffered
    inputs and outputs are not limited in size.
    """
    pass


def test_psb_block():
    pass