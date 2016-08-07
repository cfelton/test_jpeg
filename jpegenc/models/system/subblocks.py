
from random import randint
from math import floor

import myhdl
from myhdl import Signal, intbv, instance, always_comb
from rhea import Global, Clock, Signals

from .interfaces import DataStream, RGBStream
from .fifo_ready_valid import FIFOReadyValid


class VideoStreamSource(object):
    def __init__(self, resolution=(1920, 1080), refresh_rate=60):
        """A model of a video source
        This object contains an example of a video source interface and
        a process to generate the video source.

        Arguments:
            resolution (tuple): the resolution of the video source, the
                default is 1920 x 1080 (1080 rows and 1920 columns).
            refresh_rate (int): the refresh rate of the video source, the
                default is 60 Hz.

        Usage example:
            # create a video source object with the defaults
            video = VideoStreamSource()
            video_inst = video.process()

            row_buffer_inst = video.row_buffer(video, image_block)

        """
        self.resolution = resolution
        self.refresh_rate = refresh_rate
        self.start_of_frame = Signal(bool(0))
        self.end_of_frame = Signal(bool(0))
        self.pixel = RGBStream()
        # signals that monitor the current row and column
        self.currow = Signal(intbv(0, min=0, max=resolution[1]))
        self.curcol = Signal(intbv(0, min=0, max=resolution[0]))

    @myhdl.block
    def process(self, glbl):
        res = self.resolution
        num_cols, num_rows = res
        clock, reset = glbl.clock, glbl.reset

        # note, if the video rate is not a multiple of the clock then
        # the video rate will not be exact (which is fine in most )
        # cases
        ticks = int(floor(pixels_per_second / clock.frequency))

        @instance
        def model_video_source():
            tcnt, row, col = 0, 0, 0

            for ii in range(23):
                yield clock.posedge

            while True:
                # default values
                self.start_of_frame.next = False
                self.end_of_frame.next = False
                self.pixel.valid.next = False
                self.currow.next = row
                self.curcol.next = col

                if reset == reset.active:
                    row, col = 0, 0
                    continue

                tcnt += 1
                # tick count expired, output a new pixel
                if tcnt == ticks:
                    if row == 0 and col == 0:
                        self.start_of_frame.next = True
                    if row == num_rows-1 and col == num_cols-1:
                        self.end_of_frame.next = True

                    self.pixel.red.next = randint(0, self.pixel.red.max-1)
                    self.pixel.green.next = randint(0, self.pixel.green.max-1)
                    self.pixel.blue.next = randint(0, self.pixel.blue.max-1)
                    self.pixel.valid.next = True

                    row = row + 1 if row < num_rows-1 else 0
                    col = col + 1 if col < num_cols-1 else 0
                    tcnt = 0

                yield clock.posedge


class ProcessingSubblock(object):
    def __init__(self, cycles_to_process=1, latency=0, process_block=False, block_size=(8, 8)):
        """A simple model to represent a processing subblock in the jpegenc

        Arguments:
            cycles_to_process: the number of cycles to model, this is the
                number of cycles to process a sample/block.  If
                `cycles_to_process` is a 2-element tuple a random range is
                used with the tuple defining the range.

            latency: the latency of the processing, this is additional to
                the processing time, but the latency represents a pipeline,
                new samples can.  If `latency` is a 2-element tuple a random
                range is used with the tuple defining the range.

            process_block: an image block is processed vs. a sample

            block_size: the size of an image block, this is only used if
                `process_block` is True.
        """
        assert isinstance(cycles_to_process, (int, tuple))
        if isinstance(cycles_to_process, tuple):
            assert len(cycles_to_process) == 2
        assert isinstance(latency, int)
        assert isinstance(process_block, bool)
        assert isinstance(block_size, tuple) and len(block_size) == 2

        self.ctp = cycles_to_process
        self.lat = latency


    @myhdl.block
    def process(self, glbl, datain, dataout, include_fifo=False):
        assert isinstance(datain, DataStream)
        assert isinstance(dataout, DataStream)

        clock, reset = glbl.clock, glbl.reset
        ready = Signal(bool(0))

        # include an input and output fifo
        if include_fifo:
            raise NotImplementedError
            fifo_i = FIFOReadyValid()
            fifo_i_inst = fifo_i.process(glbl, datain, buffered_data_i)
            fifo_o = FIFOReadyValid()
            fifo_o_inst = fifo_o.process(glbl, buffered_data_o, dataout)
        else:
            buffered_data_i = datain
            buffered_data_o = datain

        @always_comb
        def beh_ready():
            datain.read.next = ready and buffered_data_i.ready

        @instance
        def processing_model():
            pass


        return myhdl.instances()



def color_conversion(glbl, pixel_in, pixel_out):
    """

    (arguments == ports)
    Argumentss:
        glbl (Global):
        pixel_in (PixelStream):
        pixel_out ():

    myhdl convertible
    """


def transformer_twod(glbl, sample_input, matrix_outputs, block_size=(8, 8)):
    """A two-dimension (2D) transform block

    (arguments == ports)
    Arguments:
        sample_input (PixelStream):
        matrix_outputs (ImageBlock):

    Parameters:
        block_size (tuple):

    myhdl convertible
    """
    pass


def transformer_oned(glbl, sample_input, block_output, block_size=8):
    """A one-dimension (1D) transform block

    This ~~module~~ block will stream in a sample at a time, collecting
    `block_size` input samples before producing the transform.

    (arguments == ports)
    Arguments:
        sample_input (DataStream): input sample stream
        block_output (DataBlock): output transformed block.

    Parameters:
        block_size: the size of the transform, the transform will be
            computed on ``block_size`` data points, typically the
            *N* in the math equations.

    myhdl convertible
    """
    pass
