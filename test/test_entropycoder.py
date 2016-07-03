"""This module tests the functionality and conversion of Entropy Coder"""

from myhdl import block, instance
from myhdl import intbv, ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify

from jpegenc.subblocks.rle.entropycoder import entropycoder
from jpegenc.subblocks.rle.entropycoder import entropy_encode

from jpegenc.testing import run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset


def test_entropycoder():
    """We will test the functionality of entropy coder in this block"""

    # constants for size required and width of input data
    width = 12
    size_data = (width-1).bit_length()

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # input data to the block
    data_in = Signal(intbv(0)[(width+1):].signed())

    # output data from the block
    size = Signal(intbv(0)[size_data:])
    amplitude = Signal(intbv(0)[(width+1):].signed())

    @block
    def bench_entropycoder():
        inst = entropycoder(width, clock, reset, data_in, size, amplitude)
        inst_clock = clock_driver(clock)

        @instance
        def tbstim():

            """stimulus generates inputs for entropy coder"""

            yield pulse_reset(reset, clock)

            for i in range(-2**(width-1), 2**(width-1), 1):
                data_in.next = i
                yield clock.posedge
                yield clock.posedge
                amplitude_ref, size_ref = entropy_encode(int(data_in))

                # comparing with the data present in reference
                assert size == size_ref
                assert amplitude == amplitude_ref

            raise StopSimulation

        return tbstim, inst, inst_clock

    run_testbench(bench_entropycoder)


def test_block_conversion():
    """Test bench used for conversion purpose"""

    width = 12
    size_data = int((width-1).bit_length())
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)
    data_in = Signal(intbv(0)[(width+1):].signed())
    size = Signal(intbv(0)[size_data:])
    amplitude = Signal(intbv(0)[(width+1):].signed())

    @block
    def bench_entropycoder():
        inst = entropycoder(width, clock, reset, data_in, size, amplitude)
        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_entropycoder().verify_convert() == 0
