"""Test file for RLE Double Buffer"""

from myhdl import block, StopSimulation
from myhdl import ResetSignal, Signal, delay, instance
from myhdl.conversion import verify
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import DoubleFifoBus
from jpegenc.subblocks.RLE.RleDoubleFifo.rledoublebuffer import rledoublefifo
from commons import BufferConstants
from commons import tbclock, reset_on_start, resetonstart, Constants, BufferConstants
from commons import numofbits, start_of_block, block_process, write_block, read_block

def test_doublebuffer():   
    

    @block
    def bench_doublebuffer():
        """ test bench """
        buffer_constants = BufferConstants(20, 64)
        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)
        dfifo_bus = DoubleFifoBus(buffer_constants.width)
        inst = rledoublefifo(buffer_constants, reset, clock, dfifo_bus)
        inst_clock = tbclock(clock)


        @instance
        def tbstim():
            """Set of inputs"""
            print("start simulation")
            dfifo_bus.buffer_sel.next = False
            dfifo_bus.write_enable.next = False
            dfifo_bus.read_req.next = False
            yield reset_on_start(clock, reset)
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

        return inst,inst_clock, tbstim

    inst_dbuf = bench_doublebuffer()
    inst_dbuf.config_sim(trace=False)
    inst_dbuf.run_sim()

def test_doublebuffer_conversion():

    @block
    def bench_doublebuffer_conversion():
        """ test bench """
        buffer_constants = BufferConstants(20, 64)
        clock = Signal(bool(0))
        reset = ResetSignal(0, active=1, async=True)
        dfifo_bus = DoubleFifoBus(buffer_constants.width)
        inst = rledoublefifo(buffer_constants, reset, clock, dfifo_bus)
        inst_clock = tbclock(clock)


        inst_reset = resetonstart(clock, reset)

        @instance
        def tbstim():

            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_doublebuffer_conversion().verify_convert() == 0
