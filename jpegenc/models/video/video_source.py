
from math import floor
from random import randint

import myhdl
from myhdl import Signal, intbv, instance, always_comb

from ..interfaces import DataStream, RGBStream


class VideoSource(object):
    def __init__(self, resolution=(1920, 1080), frame_rate=60, color_depth=(8, 8, 8)):
        """A model of a video source
        This object contains an example of a video source interface and
        a process to generate the video source.

        Arguments:
            resolution (tuple): the resolution of the video source, the
                default is 1920 x 1080 (1080 rows and 1920 columns).

            frame_rate (int): the frame rate of the video source, the
                default is 60 Hz (a.k.a. refresh rate).

        Attributes:
            pixel (RGBStream): the current pixel in the data stream
            rowmon (int): current row index
            colmon (int): current col index

        Usage example:
            # create a video source object with the defaults
            video = VideoStreamSource()
            video_inst = video.process()

            row_buffer_inst = video.row_buffer(video, image_block)

        """
        self.resolution = resolution
        self.frame_rate = frame_rate
        self.pixel = RGBStream(color_depth=color_depth)
        # signals that monitor the current row and column
        self.rowmon = Signal(intbv(0, min=0, max=resolution[1]))
        self.colmon = Signal(intbv(0, min=0, max=resolution[0]))

        # the number of clock ticks per pixel
        self. pixels_per_second = resolution[0] * resolution[1] * frame_rate

        # this is a counter to keep track of which pixel is being checked
        self.npixel = 0

    def get_ticks(self, clock):
        """Get the number of clock ticks per pixel"""
        pps = self.pixels_per_second
        ticks = int(floor(clock.frequency / pps))
        assert ticks > 0, "clock frequency too low {:.3f} MHz".format(
            clock.frequency / 1e6)
        return ticks

    @myhdl.block
    def process(self, glbl):
        """Generate random frames

        The default process will simply generate random frames, this
        (VideoSource) is intended to be a base class but can be used as
        a bare minimum stimulus generator.

        Args:
            glbl: interface with clock and reset

        """
        res = self.resolution
        num_cols, num_rows = res
        clock, reset = glbl.clock, glbl.reset

        # note, if the video rate is not a multiple of the clock then
        # the video rate will not be exact (which is fine)
        ticks = self.get_ticks(clock)
        print("{} clock ticks per pixel".format(ticks))

        @instance
        def model_video_source():
            tcnt, row, col = 0, 0, 0

            for ii in range(23):
                yield clock.posedge

            while True:
                # default values
                self.pixel.start_of_frame.next = False
                self.pixel.end_of_frame.next = False
                self.pixel.valid.next = False
                self.rowmon.next = row
                self.colmon.next = col

                if reset == reset.active:
                    row, col = 0, 0
                    continue

                tcnt += 1
                # tick count expired, output a new pixel
                if tcnt >= ticks:
                    if row == 0 and col == 0:
                        self.pixel.start_of_frame.next = True
                    if row == num_rows-1 and col == num_cols-1:
                        self.pixel.end_of_frame.next = True

                    # set the current pixel value
                    self.pixel_value(row, col)
                    self.pixel.valid.next = True

                    row = row + 1 if row < num_rows-1 else 0
                    col = col + 1 if col < num_cols-1 else 0
                    tcnt = 0

                yield clock.posedge

        return myhdl.instances()

    def pixel_value(self, row, col):
        """Get the pixel value for the video source.
        Given the ``row`` and ``col`` address return the RGB value
        for the pixel.  The default is to return a random value
        (will not be consistent across calls).  This method should
        be implemented (overridden) for each video source type.
        """
        self.pixel.red.next = r = randint(0, self.pixel.red.max - 1)
        self.pixel.green.next = g = randint(0, self.pixel.green.max - 1)
        self.pixel.blue.next = b = randint(0, self.pixel.blue.max - 1)

        return r, g, b

    def check_pixel(self, rgb, npixel=None):
        """Check a pixel

        Args:
            rgb (list):
            npixel:

        Returns:

        """
        raise NotImplementedError

    def check_buffer(self, buffer, frame=0, offset=0):
        raise NotImplementedError
