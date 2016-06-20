"""Test file for RLE Double Buffer"""

from myhdl import block, StopSimulation
from myhdl import ResetSignal, Signal, delay, instance
#   from myhdl.conversion import verify
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import DoubleFifoBus
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import rledoublefifo
from commons import BufferConstants
        
@block
def test():
    """ test bench """
    buffer_constants = BufferConstants(20, 64)
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)
    dfifo_bus = DoubleFifoBus(buffer_constants.width)
    dut = rledoublefifo(buffer_constants, reset, clock, dfifo_bus)

    @instance
    def tbclock():
        """ Clock generator """
        clock.next = False
        while True:
            yield delay(10)
            clock.next = not clock

    @instance
    def tbstim():
        """Set of inputs"""
        print("start simulation")
        dfifo_bus.buffer_sel.next = False
        dfifo_bus.write_enable.next = False
        dfifo_bus.read_req.next = False
        reset.next = True
        yield delay(20)
        reset.next = False
        yield clock.posedge
        assert dfifo_bus.fifo_empty

        dfifo_bus.buffer_sel.next = False
        yield clock.posedge

        dfifo_bus.write_enable.next = True
        dfifo_bus.data_in.next = -1 and 0xFF
        yield clock.posedge
        dfifo_bus.write_enable.next = False
        yield clock.posedge
        assert dfifo_bus.fifo_empty

        dfifo_bus.write_enable.next = True
        dfifo_bus.data_in.next = 0xA1
        yield clock.posedge
        dfifo_bus.write_enable.next = False
        yield clock.posedge
        assert dfifo_bus.fifo_empty

        dfifo_bus.write_enable.next = True
        dfifo_bus.data_in.next = 0x11
        yield clock.posedge
        dfifo_bus.write_enable.next = False
        yield clock.posedge

        dfifo_bus.write_enable.next = True
        dfifo_bus.data_in.next = 0x101
        yield clock.posedge
        dfifo_bus.write_enable.next = False
        yield clock.posedge

        for test_cases in range(64):
            if test_cases < 28:
                dfifo_bus.buffer_sel.next = False
                yield clock.posedge
            else:
                dfifo_bus.buffer_sel.next = True
                yield clock.posedge

            dfifo_bus.write_enable.next = True
            dfifo_bus.data_in.next = test_cases
            yield clock.posedge
            dfifo_bus.write_enable.next = False
            yield clock.posedge

        dfifo_bus.read_req.next = True
        yield clock.posedge
        assert dfifo_bus.data_out and -1 == -1
        dfifo_bus.read_req.next = False

        dfifo_bus.buffer_sel.next = True
        yield clock.posedge

        dfifo_bus.read_req.next = True
        yield clock.posedge
        assert dfifo_bus.data_out == 0xA1
        dfifo_bus.read_req.next = False

        dfifo_bus.buffer_sel.next = True
        yield clock.posedge

        dfifo_bus.read_req.next = True
        yield clock.posedge
        assert dfifo_bus.data_out == 0x11
        dfifo_bus.read_req.next = False

        dfifo_bus.buffer_sel.next = True
        yield clock.posedge

        dfifo_bus.read_req.next = True
        yield clock.posedge
        assert dfifo_bus.data_out == 0x101
        dfifo_bus.read_req.next = False

        for test_cases in range(64):
            if test_cases < 28:
                dfifo_bus.buffer_sel.next = True
                yield clock.posedge
            else:
                dfifo_bus.buffer_sel.next = False
                yield clock.posedge

            dfifo_bus.read_req.next = True
            yield clock.posedge
            assert dfifo_bus.data_out == test_cases
            dfifo_bus.read_req.next = False

        yield clock.posedge

        assert dfifo_bus.fifo_empty

        raise StopSimulation

    return dut, tbclock, tbstim


def testbench():
    """Run Simulation from here"""

    inst = test()
    inst.config_sim(trace=False)
    inst.run_sim()

    # verify.simulator = 'iverilog'
    # assert test().verify_convert() == 0

    # verify.simulator = 'ghdl'
    # assert test().verify_convert() == 0

if __name__ == '__main__':
    testbench()
