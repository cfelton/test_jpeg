"""This module is the testbench for the
    divider used in Quantiser module"""

from myhdl import block, instance
from myhdl import intbv, ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify

from jpegenc.subblocks.quantizer.divider import divider
from common import tbclock, resetonstart, reset_on_start
from common import divider_ref


def test_divider():
    """The functionality of the divider is tested here"""

    # clock and reset signals
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # dividend, divisor, quotient signals declared
    dividend = Signal(intbv(0)[12:].signed())
    divisor = Signal(intbv(0)[8:])
    quotient = Signal(intbv(0)[12:].signed())

    # compute data width
    width_data = len(dividend)-1

    @block
    def bench_divider():
        """The module where we pass tests into divider block"""

        # instantiation of clock and divider
        inst = divider(reset, clock, dividend, divisor, quotient)
        inst_clock = tbclock(clock)

        @instance
        def tbstim():
            """Test cases are given here"""

            # reset signal
            yield reset_on_start(clock, reset)
            list_output = []
            list_output_ref = []

            # all the possible tests from -2048 to 2048 given here
            for dividend_temp in range(-5, 5, 1):
                for divisor_temp in range(0, 256, 1):
                    dividend.next = dividend_temp
                    divisor.next = divisor_temp
                    result = divider_ref(dividend_temp, divisor_temp)
                    list_output_ref.append(result)
                    yield clock.posedge
                    list_output.append(int(quotient))

            yield clock.posedge
            list_output.append(int(quotient))
            yield clock.posedge
            list_output.append(int(quotient))
            yield clock.posedge
            list_output.append(int(quotient))
            yield clock.posedge
            list_output.append(int(quotient))

            # pop the zeroes stored in the list because of pipelining
            list_output.pop(0)
            list_output.pop(0)
            list_output.pop(0)
            list_output.pop(0)

            # compare reference design divider output with that of HDL divider
            for item1, item2 in zip(list_output, list_output_ref):
                print ("quotient %d quotient_ref %d" % (item1, item2))
                assert item1 == item2

            raise StopSimulation

        return tbstim, inst, inst_clock

    inst1 = bench_divider()
    inst1.config_sim(trace=False)
    inst1.run_sim()


def test_block_conversion():
    """Test bench used for conversion purpose"""

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    dividend = Signal(intbv(0)[12:].signed())
    divisor = Signal(intbv(0)[8:])
    quotient = Signal(intbv(0)[12:].signed())

    @block
    def bench_divider():
        """Wrapper used for conversion purpose"""

        # instantiatiom of divider, clock and reset
        inst = divider(reset, clock, dividend, divisor, quotient)
        inst_clock = tbclock(clock)
        inst_reset = resetonstart(clock, reset)

        @instance
        def tbstim():
            """Dummy tests to convert the module"""
            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_divider().verify_convert() == 0
