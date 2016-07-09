<<<<<<< HEAD
'''This module tests the functionality and conversion of Entropy Coder'''
=======
"""This module tests the functionality and conversion of Entropy Coder"""
>>>>>>> upstream/master

from myhdl import block, instance
from myhdl import intbv, ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify
<<<<<<< HEAD
from jpegenc.subblocks.RLE.RLECore.entropycoder import entropycoder
from common import tbclock, reset_on_start, entropy_encode, numofbits
from common import resetonstart
=======

from jpegenc.subblocks.rle.entropycoder import entropycoder
from jpegenc.subblocks.rle.entropycoder import entropy_encode

from jpegenc.testing import run_testbench
from jpegenc.testing import clock_driver, reset_on_start, pulse_reset
>>>>>>> upstream/master


def test_entropycoder():
    """We will test the functionality of entropy coder in this block"""

    # constants for size required and width of input data
    width = 12
<<<<<<< HEAD
    size_data = (numofbits(width-1))
=======
    size_data = (width-1).bit_length()
>>>>>>> upstream/master

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
<<<<<<< HEAD
        inst_clock = tbclock(clock)
=======
        inst_clock = clock_driver(clock)
>>>>>>> upstream/master

        @instance
        def tbstim():

            """stimulus generates inputs for entropy coder"""

<<<<<<< HEAD
            yield reset_on_start(clock, reset)
=======
            yield pulse_reset(reset, clock)
>>>>>>> upstream/master

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

<<<<<<< HEAD
    inst1 = bench_entropycoder()
    inst1.config_sim(trace=False)
    inst1.run_sim()
=======
    run_testbench(bench_entropycoder)
>>>>>>> upstream/master


def test_block_conversion():
    """Test bench used for conversion purpose"""

    width = 12
<<<<<<< HEAD
    size_data = int(numofbits(width-1))
=======
    size_data = int((width-1).bit_length())
>>>>>>> upstream/master
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)
    data_in = Signal(intbv(0)[(width+1):].signed())
    size = Signal(intbv(0)[size_data:])
    amplitude = Signal(intbv(0)[(width+1):].signed())

    @block
    def bench_entropycoder():
        inst = entropycoder(width, clock, reset, data_in, size, amplitude)
<<<<<<< HEAD
        inst_clock = tbclock(clock)
        inst_reset = resetonstart(clock, reset)
=======
        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)
>>>>>>> upstream/master

        @instance
        def tbstim():
            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_entropycoder().verify_convert() == 0
