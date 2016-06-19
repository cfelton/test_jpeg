''' testbench for entropy coder '''

from myhdl import block, delay
from myhdl import instance
from myhdl import intbv, ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify
from jpegenc.subblocks.RLE.RLECore.entropycoder import entropycoder
from commons import tbclock, reset_on_start, entropy_encode, numofbits


@block
def resetonstart(clock, reset):
    """reset block used for verification purpose"""
    @instance
    def reset_button():
        reset.next = True
        yield delay(40)
        yield clock.posedge
        reset.next = False
    return reset_button


def test_entropycoder():
    """We will test the entropy coder in this block"""
    
    WIDTH = 12
    SIZE = int(numofbits(WIDTH-1))
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)
    data_in = Signal(intbv(0)[(WIDTH+1):].signed())
    size = Signal(intbv(0)[SIZE:])
    amplitude = Signal(intbv(0)[(WIDTH+1):].signed())

    @block
    def bench_entropycoder():
        inst = entropycoder(WIDTH, clock, reset, data_in, size, amplitude)
        inst_clock = tbclock(clock)

        @instance
        def tbstim():

            """ stimulus generates inputs for entropy coder """

            yield reset_on_start(clock, reset)

            for i in range(-2**(WIDTH-1), 2**(WIDTH-1), 1):
                data_in.next = i
                yield clock.posedge
                yield clock.posedge
                amplitude_ref, size_ref = entropy_encode(data_in)
                # comparing with the data present in reference
                assert size == size_ref
                assert amplitude == amplitude_ref

            raise StopSimulation

        return tbstim, inst, inst_clock

    inst1 = bench_entropycoder()
    inst1.config_sim(trace=False)
    inst1.run_sim()


def test_block_conversion():
    """Test bench used for conversion purpose"""

    WIDTH = 12
    SIZE = int(numofbits(WIDTH-1))
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)
    data_in = Signal(intbv(0)[(WIDTH+1):].signed())
    size = Signal(intbv(0)[SIZE:])
    amplitude = Signal(intbv(0)[(WIDTH+1):].signed())

    @block
    def bench_entropycoder():
        inst = entropycoder(WIDTH, clock, reset, data_in, size, amplitude)
        inst_clock = tbclock(clock)
        inst_reset = resetonstart(clock, reset)

        @instance
        def tbstim():
            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_entropycoder().verify_convert() == 0
