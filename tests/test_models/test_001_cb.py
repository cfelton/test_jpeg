
import myhdl
from myhdl import instance, StopSimulation
from rhea import Global, Clock

from jpegenc.models.video import ColorBars
from jpegenc.testing import run_testbench


def test_colorbars():
    resolution = (1920, 1080)
    frame_rate = 60
    color_depth = (8, 8, 8)

    @myhdl.block
    def bench():
        clock = Clock(0, frequency=125e6)
        glbl = Global(clock)
        ck_drv = clock.gen()

        video_source = ColorBars(
            resolution=resolution, color_depth=color_depth,
            frame_rate=frame_rate
        )
        vd_proc = video_source.process(glbl)
        pixel = video_source.pixel

        @instance
        def tbstim():
            # only capture a subset of pixels for this test
            npx = 128
            pcnt, tcnt, timeout = 0, 0, 4*npx

            # the video source has a pixel interface, indicate to
            # the video source downstream is read to get pixels
            pixel.ready.next = True

            while pcnt < npx and tcnt < timeout:
                yield clock.posedge
                tcnt += 1
                if pixel.valid:
                    pcnt += 1

            assert pcnt == npx
            raise StopSimulation

        return myhdl.instances()

    run_testbench(bench, trace=True, bench_id='colorbars')

