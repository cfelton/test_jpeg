
import myhdl
from myhdl import Signal, intbv, instance, always_comb
from rhea import Global, Clock, Signals


class FIFOReadyValid(object):
    def __init__(self):
        """A simple ready-valid FIFO model (no size restriction)

        This FIFO is used to model a ready-valid FIFO that controls the
        flow of data in the encoder.  The FIFOs will not restrict the
        size, the flow stop will need to come from.
        """
        self.max_count = 0
        self._fifo = []

    @property
    def count(self):
        return len(self._fifo)

    @myhdl.block
    def process(self, glbl, datain, dataout):
        assert type(datain) == type(dataout), \
            "FIFOReadyValid only supports same type interface in and out"

        clock = glbl.clock

        @instance
        def model_fifo():
            while True:
                datain.ready.next = True
                if len(self._fifo) > 0:
                    do = self._fifo[0]
                else:
                    do = 0
                dataout.data.next = do

                yield clock.posedge

                if datain.valid:
                    # @todo: push a complete copy of the data interface
                    #        need to maintain, start-of-frame, end-of-frame
                    #        and other signals and state
                    self._fifo.append(int(datain.data))
                    self.max_count = max(self.max_count, len(self._fifo))

                if len(self._fifo) > 0:
                    self.valid.next = True
                else:
                    self.valid.next = False

                # if the downstream is ready, above valid would be set
                # pop the read data from the FIFO.
                if dataout.ready and len(self._fifo) > 0:
                    self._fifo.pop(0)

        return myhdl.instances()
