
import myhdl
from myhdl import instance

from ..interfaces import DataStream
from .video_source import VideoSource


class BitstreamDevourer(object):
    def __init__(self, source, encoder=None):
        assert isinstance(source, VideoSource)
        self.source = source
        self.resolution = source.resolution
        self.encoder = encoder

        # keep track of the data words captured
        self.num_data = 0

    @myhdl.block
    def process(self, glbl, data):
        """

        Args:
            glbl (Global): global interface, contains clock and reset
            data (DataStream): final bitstream

        """
        assert isinstance(data, DataStream)
        clock, reset = glbl.clock, glbl.reset
        src = self.source
        self.num_data = 0

        @instance
        def mdl_simple_capture():
            """Temp capture and display"""
            # ready to receive the data
            src.pixel.ready.next = True
            while True:
                yield clock.posedge
                if src.pixel.valid:
                    print("  [BD]: {:03X}".format(src.pixel.data))
                    self.num_data += 1

        return myhdl.instances()

