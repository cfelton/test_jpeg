''' testbench for entropy coder '''

from myhdl import block, delay
from myhdl import instance
from myhdl import intbv, ResetSignal, Signal, StopSimulation
from jpegenc.subblocks.RLE.RLECore.entropycoder import entropycoder

# declared constants
WIDTH = 12
SIZE = 4


@block
def test():

    '''sequential block for testing entropy coder '''

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)
    data_in = Signal(intbv(0)[(WIDTH+1):].signed())
    size = Signal(intbv(0)[SIZE:])
    amplitude = Signal(intbv(0)[(WIDTH+1):].signed())

    inst = entropycoder(clock, reset, data_in, size, amplitude)

    @instance
    def tbclock():

        ''' instance that generates clock '''
        clock.next = 0
        while True:
            yield delay(10)
            clock.next = not clock

    @instance
    def tbsim():

        ''' instance that generates input for entropy coder '''

        reset.next = True
        yield delay(20)
        reset.next = False
        yield clock.posedge

        for i in range(-2045, 2045, 1):
            data_in.next = i
            yield clock.posedge
            yield clock.posedge

        raise StopSimulation

    return tbsim, tbclock, inst


def bench():

    ''' testbench begins here '''
    inst1 = test()
    inst1.config_sim(trace=False)
    inst1.run_sim()


if __name__ == '__main__':
    bench()
