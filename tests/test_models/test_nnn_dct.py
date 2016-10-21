
import myhdl
from myhdl import instance, delay, StopSimulation
from rhea import Global, Clock

from jpegenc.models.subblocks import DCTDataFlow
from jpegenc.models.video import ColorBars
from jpegenc.models.video import BitstreamDevourer

from jpegenc.testing import run_testbench


def test_dct_data_flow():

    resolution = (1920, 1080)
    frame_rate = 60
    color_depth = (8, 8, 8)

    clock = Clock(0, frequency=125e6)
    glbl = Global(clock)
    video_source = ColorBars(resolution, color_depth, frame_rate)
    dct = DCTDataFlow()
    bit_sink = BitstreamDevourer(source=video_source, encoder=None)

    @myhdl.block
    def bench():
        ck_drv = clock.gen()

        vd_proc = video_source(glbl)
        pixel_i = video_source.pixel
        pixel_o = video_source.pixel.copy()

        dct_proc = dct(glbl, pixel_i, pixel_o)
        vk_proc = bit_sink(glbl, pixel_o)
        bd = bit_sink

        @instance
        def tbstim():
            npxl = 3*64   # get 3 blocks
            tcnt, timeout = 0, 4*npxl

            while bd.num_data_words < npxl and tcnt < timeout:
                yield clock.posedge
                tcnt += 1

            # not concerned about an actual amount, just that it
            # received at least the number specified
            assert bd.num_data_words >= npxl

            raise StopSimulation

        # set a name for the instances for tracing, otherwise the
        # "process" method in each of the objects results in the
        # same extended name for all the processes.
        # ck_drv.name = 'clock_driver'
        # vd_proc.name = 'video_source'
        # dct_proc.name = 'dct_data_flow'
        # vk_proc.name = 'bit_sink'

        return myhdl.instances()

    run_testbench(bench, trace=True, bench_id='dct_data_flow')
