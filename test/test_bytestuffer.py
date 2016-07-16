"""This module tests the functionality and conversion of Entropy Coder"""

from myhdl import block, instance
from myhdl import intbv, ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify

from jpegenc.subblocks.bytestuffer import bytestuffer, BSInputDataStream
from jpegenc.subblocks.bytestuffer import BScntrl, BSOutputDataStream


from jpegenc.testing import run_testbench
from jpegenc.testing import (clock_driver, reset_on_start,
                             pulse_reset, toggle_signal)


def test_bytestuffer():
    """
    We will test the functionality of bytestuffer in this block

    Constants:

    width_addr_out : maximum adress width of the output RAM
    width_out      : width of the data in the ouput RAM

    """

    # width of the input data or output data
    width_data = 8
    # maximum address width of output RAM
    width_addr_out = 24

    # clock and reset signals
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # input, output and control interfaces
    bs_in_stream = BSInputDataStream(width_data)
    assert isinstance(bs_in_stream, BSInputDataStream)

    bs_out_stream = BSOutputDataStream(width_data, width_addr_out)
    assert isinstance(bs_out_stream, BSOutputDataStream)

    bs_cntrl = BScntrl()
    assert isinstance(bs_cntrl, BScntrl)

    num_enc_bytes = Signal(intbv(0)[width_addr_out:])

    @block
    def bench_bytestuffer():
        """This bench is used to test the functionality"""

        # instantiate module and clock
        inst = bytestuffer(
            clock, reset, bs_in_stream, bs_out_stream, bs_cntrl, num_enc_bytes)

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """stimulus generates inputs for byte stuffer"""

            # reset the module
            yield pulse_reset(reset, clock)
            yield toggle_signal(bs_cntrl.start, clock)
            yield clock.posedge

            # send input data
            for i in range(64):
                # send 0xFF bytes
                if i % 5 == 0:
                    bs_in_stream.data_in.next = 0xFF
                # send other bytes
                else:
                    bs_in_stream.data_in.next = i

                yield clock.posedge
                if bs_out_stream.data_valid:
                    print ("output data is %d" % bs_out_stream.byte)

                # assert fifo empty when all the inputs are over
                if i == 63:
                    bs_in_stream.fifo_empty.next = True

                for j in range(3):
                    yield clock.posedge

                if bs_out_stream.data_valid:
                    print ("output data is %d" % bs_out_stream.byte)

            yield toggle_signal(bs_cntrl.sof, clock)
            # if last byte is 0xFF. Print the zero's stuffed
            if bs_out_stream.data_valid:
                print ("output data is %d" % bs_out_stream.byte)

            print ("total encoded bytes is %d" % num_enc_bytes)
            raise StopSimulation

        return tbstim, inst, inst_clock

    run_testbench(bench_bytestuffer)


def test_block_conversion():
    """Test bench used for conversion purpose"""

    # width of the input data or output data
    width_data = 8
    # maximum address width of output RAM
    width_addr_out = 24

    # clock and reset signals
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # input, output and control interfaces
    bs_in_stream = BSInputDataStream(width_data)
    assert isinstance(bs_in_stream, BSInputDataStream)

    bs_out_stream = BSOutputDataStream(width_data, width_addr_out)
    assert isinstance(bs_out_stream, BSOutputDataStream)

    bs_cntrl = BScntrl()
    assert isinstance(bs_cntrl, BScntrl)

    num_enc_bytes = Signal(intbv(0)[width_addr_out:])

    @block
    def bench_entropycoder():
        """This bench is used for conversion purpose"""

        # instantiate module, clock and reset
        inst = bytestuffer(
            clock, reset, bs_in_stream, bs_out_stream, bs_cntrl, num_enc_bytes)

        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            """dummy tests for conversion purpose"""
            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    # verify conversion using iverilog
    verify.simulator = 'iverilog'
    assert bench_entropycoder().verify_convert() == 0
