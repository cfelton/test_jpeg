"""
Test file for doublebuffer to
check its conversion and funtioning

"""

from myhdl import block, StopSimulation
from myhdl import ResetSignal, Signal, instance
from myhdl.conversion import verify

from rhea.system import FIFOBus
from jpegenc.subblocks.huffman.doublebuffer import doublefifo

from jpegenc.testing import run_testbench
from jpegenc.testing import clock_driver, pulse_reset, reset_on_start


def test_doublebuffer():
    """The functionality of Double Buffer is tested here"""

    @block
    def bench_doublebuffer():
        """This bench is used to send test cases into module"""

        # instantiation of clock and reset
        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        # buffer selection port instantiation
        buffer_sel = Signal(bool(0))

        # input data width and depth of FIFO(double)
        width_data = 20
        width_depth = 64

        # instantiation of FIFOBus, clock and rledoublefifo
        dfifo_bus = FIFOBus(width=width_data)

        inst = doublefifo(
            clock, reset, dfifo_bus, buffer_sel, depth=width_depth)

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """write data inputs to double buffer"""

            print("start simulation")

            # disable read and write
            dfifo_bus.write.next = False
            dfifo_bus.read.next = False

            # reset before sending data
            yield pulse_reset(reset, clock)

            # check if FIFO is empty
            assert dfifo_bus.empty

            # select first buffer
            buffer_sel.next = False
            yield clock.posedge

            # write first data into double buffer
            dfifo_bus.write.next = True

            # convert signed number to unsigned
            dfifo_bus.write_data.next = -1 and 0xFF
            yield clock.posedge
            dfifo_bus.write.next = False
            yield clock.posedge
            assert dfifo_bus.empty

            # write data into double buffer
            dfifo_bus.write.next = True
            dfifo_bus.write_data.next = 0xA1
            yield clock.posedge
            dfifo_bus.write.next = False
            yield clock.posedge
            assert dfifo_bus.empty

            # write data into rle double buffer
            dfifo_bus.write.next = True
            dfifo_bus.write_data.next = 0x11
            yield clock.posedge
            dfifo_bus.write.next = False
            yield clock.posedge

            # write data into rle double buffer
            dfifo_bus.write.next = True
            dfifo_bus.write_data.next = 0x101
            yield clock.posedge
            dfifo_bus.write.next = False
            yield clock.posedge

            # write data into rle double buffer
            for test_cases in range(64):
                if test_cases < 28:
                    buffer_sel.next = False
                    yield clock.posedge
                else:
                    buffer_sel.next = True
                    yield clock.posedge

                dfifo_bus.write.next = True
                dfifo_bus.write_data.next = test_cases
                yield clock.posedge
                dfifo_bus.write.next = False
                yield clock.posedge

            print ("printing second FIFO outputs")
            # read data
            dfifo_bus.read.next = True
            yield clock.posedge
            dfifo_bus.read.next = False
            yield clock.posedge
            print ("%d" % dfifo_bus.read_data)

            dfifo_bus.read.next = True
            yield clock.posedge
            dfifo_bus.read.next = False
            yield clock.posedge
            print ("%d" % dfifo_bus.read_data)

            dfifo_bus.read.next = True
            yield clock.posedge
            dfifo_bus.read.next = False
            yield clock.posedge
            print ("%d" % dfifo_bus.read_data)

            for _ in range(29):
                dfifo_bus.read.next = True
                yield clock.posedge
                dfifo_bus.read.next = False
                yield clock.posedge
                print ("%d" % dfifo_bus.read_data)

            buffer_sel.next = False
            yield clock.posedge

            print ("printing first FIFO outputs")

            # read some more data
            dfifo_bus.read.next = True
            yield clock.posedge
            dfifo_bus.read.next = False
            yield clock.posedge
            print ("%d" % dfifo_bus.read_data)

            dfifo_bus.read.next = True
            yield clock.posedge
            dfifo_bus.read.next = False
            yield clock.posedge
            print ("%d" % dfifo_bus.read_data)

            dfifo_bus.read.next = True
            yield clock.posedge
            dfifo_bus.read.next = False
            yield clock.posedge
            print ("%d" % dfifo_bus.read_data)

            for _ in range(33):
                dfifo_bus.read.next = True
                yield clock.posedge
                dfifo_bus.read.next = False
                yield clock.posedge
                print ("%d" % dfifo_bus.read_data)

            raise StopSimulation

        return inst, inst_clock, tbstim

    run_testbench(bench_doublebuffer)


def test_doublebuffer_conversion():
    """This block checks the conversion of Rle Double Fifo"""

    @block
    def bench_doublebuffer_conversion():
        """test bench for conversion"""

        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)

        buffer_sel = Signal(bool(0))

        width_data = 20
        width_depth = 64
        # instantiation of fifo-bus, clock and rledoublefifo
        dfifo_bus = FIFOBus(width=width_data)

        inst = doublefifo(
            clock, reset, dfifo_bus, buffer_sel, depth=width_depth)

        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            """some tests for conversion purpose"""

            # select first buffer
            buffer_sel.next = False
            yield clock.posedge

            # write first data into double buffer
            dfifo_bus.write.next = True

            # convert signed number to unsigned
            dfifo_bus.write_data.next = 3
            yield clock.posedge
            dfifo_bus.write.next = False
            yield clock.posedge
            assert dfifo_bus.empty

            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_doublebuffer_conversion().verify_convert() == 0
