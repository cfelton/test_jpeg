
from random import randint
from math import floor

import myhdl
from myhdl import Signal, intbv, instance, always_comb
from rhea import Global, Clock, Signals

from .interfaces import DataStream, RGBStream
from .fifo_ready_valid import FIFOReadyValid


class ProcessingSubblock(object):
    def __init__(self, cycles_to_process=1, block_size=None, buffered=False):
        """A simple model to represent a processing subblock in the jpegenc

        Arguments:
            cycles_to_process: the number of cycles to model, this is the
                number of cycles to process a sample/block.  If
                `cycles_to_process` is a 2-element tuple a random range is
                used with the tuple defining the range.

            @todo: latency is the same (essentially) as cycles_to_process, need
                   some other argument to indicated successive output gaps,
                   no gap fully pipelined (latency == ctp) if gap == ctp not
                   pipelined and stalls in between, the same for sample or
                   block processing.
            ~~latency: the latency of the processing, this is additional to
                the processing time, but the latency represents a pipeline,
                new samples can.  If `latency` is a 2-element tuple a random
                range is used with the tuple defining the range.~~

            block_size: the size of an image block, if None process
                sample by sample.

            buffered
        """
        assert isinstance(cycles_to_process, (int, tuple))
        if isinstance(cycles_to_process, tuple):
            assert len(cycles_to_process) == 2
        # assert isinstance(latency, int)
        # assert isinstance(process_block, bool)
        assert isinstance(block_size, tuple) and len(block_size) == 2
        assert isinstance(buffered, bool)

        # the cycles to process is the same as latency
        self.ctp = cycles_to_process
        # self.lat = latency
        self.block_size = block_size
        self.buffered = buffered

        if buffered:
            # @todo: use buffer_size argument to limit buffer size
            #        test overruns
            self.fifo_i = FIFOReadyValid()
            self.fifo_o = FIFOReadyValid()
        else:
            self.fifo_i = None
            self.fifo_o = None

    @myhdl.block
    def process(self, glbl, datain, dataout):
        assert isinstance(datain, DataStream)
        assert isinstance(dataout, DataStream)

        clock, reset = glbl.clock, glbl.reset
        ready = Signal(bool(0))

        # include an input and output fifo
        if self.buffered:
            # @todo: implement the FIFO
            raise NotImplementedError

            # @todo: the interfaces need to override copy ...
            buffered_data_i = type(datain)()
            buffered_data_o = type(datain)()

            fifo_i = self.fifo_i
            fifo_i_inst = fifo_i.process(glbl, datain, buffered_data_i)
            fifo_o = self.fifo_o
            fifo_o_inst = fifo_o.process(glbl, buffered_data_o, dataout)
        else:
            buffered_data_i = datain
            buffered_data_o = None

        @always_comb
        def beh_ready():
            # tell upstream ready to process
            if self.buffered:
                datain.ready.next = ready and buffered_data_i.ready
            else:
                datain.ready.next = ready

        # need an intermediate to hold the signal values
        # @todo: the interfaces need to overload __copy__,
        #        To make this generic this needs a new (copy) instance
        #        with all the same attributes/properties, the current
        #        only uses the default.
        dataproc = type(datain)()

        @instance
        def processing_model():
            ready.next = True
            while True:
                # datain -> dataproc -> dataout
                dataproc.assign(datain)
                # @todo: fixed at 1 cycle for now
                #        if the latency is less than
                # for nn in range(self.ctp):
                yield clock.posedge
                dataout.assign(dataproc)

        return myhdl.instances()
