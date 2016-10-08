
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

        @instance
        def mdl_simple_capture():
            """Temp capture and display"""
            # ready to receive the data
            src.pixel.ready.next = True
            while True:
                yield clock.posedge
                if src.pixel.valid:
                    print("  [BD]: {:03X}".format(src.pixel.data))

        return myhdl.instances()

