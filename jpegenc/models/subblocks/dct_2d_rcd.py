
from .. import ProcessingSubblock


class DCTDataFlow(ProcessingSubblock):
    def __init__(self, block_size=(8, 8)):
        """Emulate the dataflow of a row-column decomposition DCT.

        Args:
            block_size (tuple:
        """
        ncyc = 2 * block_size[0] * block_size[0]
        self.ctp = ncyc
        self.pipe = True

        # @todo: output should be buffered, not inpput
        super(DCTDataFlow, self).__init__(
            cycles_to_process=self.ctp,
            pipelined=self.pipe,
            block_size=block_size,
            buffered=False
        )

