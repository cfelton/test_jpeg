"""This module tests the functionality and conversion of Entropy Coder"""

from myhdl import block, instance
from myhdl import intbv, ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify

from jpegenc.subblocks.rle.entropycoder import entropycoder
from jpegenc.subblocks.rle.entropycoder import entropy_encode

from jpegenc.testing import run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset


def test_entropycoder():
    """
    We will test the functionality of entropy coder in this block

    constants:

    width_data : width of the input data
    size_data : size required to store the data

    """

    # width of the input data
    width_data = 12

    # size required to store input data
    size_data = (width_data-1).bit_length()

    # clock and reset signals
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # declaration of input signal
    data_in = Signal(intbv(0)[width_data:].signed())

    # declaration of output signals
    size = Signal(intbv(0)[size_data:])
    amplitude = Signal(intbv(0)[width_data:].signed())

    @block
    def bench_entropycoder():
        """This bench is used to test the functionality"""

        # instantiate module and clock
        inst = entropycoder(clock, reset, data_in, size, amplitude)
        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """stimulus generates inputs for entropy coder"""

            # reset the module
            yield pulse_reset(reset, clock)

            # send input test cases into the module
            for i in range(-2**(width_data-1)+1, 2**(width_data-1), 1):
                data_in.next = i
                yield clock.posedge
                yield clock.posedge

                # extract results from reference design
                amplitude_ref, size_ref = entropy_encode(int(data_in))

                # comparing reference and module results
                assert size == size_ref
                assert amplitude == amplitude_ref

            raise StopSimulation

        return tbstim, inst, inst_clock

    run_testbench(bench_entropycoder)


def test_block_conversion():
    """Test bench used for conversion purpose"""

    # width of input data
    width_data = 12

    # size required to store ouputs
    size_data = (width_data-1).bit_length()

    # clock and reset signal declaration
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # input and output signal declarations
    data_in = Signal(intbv(0)[width_data:].signed())
    size = Signal(intbv(0)[size_data:])
    amplitude = Signal(intbv(0)[width_data:].signed())

    @block
    def bench_entropycoder():
        """This bench is used for conversion purpose"""

        # instantiate module, clock and reset
        inst = entropycoder(clock, reset, data_in, size, amplitude)
        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            """dummy tests for conversion purpose"""

            data_in.next = 7
            yield clock.posedge
            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    # verify conversion using iverilog
    verify.simulator = 'iverilog'
    assert bench_entropycoder().verify_convert() == 0
