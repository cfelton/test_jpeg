

import myhdl
from myhdl import Signal, instance

from jpegenc.interfaces import ObjectWithBlocks, DataStream
from .video_source import VideoSource


class BitstreamDevourer(ObjectWithBlocks):
    def __init__(self, source, encoder=None):
        """

        Args:
            source (VideoSource): the original video/image source to
                compare the decoded bitstream to.
            encoder (CODEC):
        """
        assert isinstance(source, (VideoSource, type(None)))
        super(BitstreamDevourer, self).__init__(name='bitdevour')

        self.source = source
        if source is not None:
            self.resolution = source.resolution
        self.encoder = encoder
        self.bits = None

        # keep track of the data words captured
        self.num_data_words = Signal(0)

    @myhdl.block
    def process(self, glbl, bits):
        """

        Args:
            glbl (Global): global interface, contains clock and reset
            bits (DataStream): final bitstream

        """
        assert isinstance(bits, DataStream)
        clock, reset = glbl.clock, glbl.reset
        self.bits = bits
        src = self.source
        ndw = self.num_data_words

        @instance
        def mdl_simple_capture():
            """Temp capture and display"""
            # ready to receive the data
            bits.ready.next = True

            while True:
                yield clock.posedge
                if bits.valid:
                    print("  [BD][{:5d}]: {:06X}".format(
                        int(ndw), int(bits.data)))
                    ndw.next = ndw + 1

        return myhdl.instances()

