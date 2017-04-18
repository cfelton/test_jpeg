from myhdl import *
from myhdl.conversion import *

from fifobus import *
from Fifo import *
from test_utils import *
from RleDoubleFifo import *




@block
def test():

    clk = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)
    data_in = Signal(intbv(0)[20:])
    wren = Signal(bool(0))
    buf_sel = Signal(bool(0))
    rd_req = Signal(bool(0))
    fifo_empty = Signal(bool(0))
    data_out = Signal(intbv()[20:])
    dut = rledoublefifo(clk, reset, data_in, wren, buf_sel, rd_req, fifo_empty, data_out)

    @instance
    def tbclk():
        clk.next=0
        while True:
            yield delay(5)
            clk.next = not clk


    @instance
    def tbstim():

        print ("Start Simulation")

        buf_sel.next = False
        wren.next = False
        rd_req.next = False
        reset.next = True
        yield delay(20) 
        reset.next = False
        yield clk.posedge
        assert fifo_empty

        buf_sel.next = False  
        yield clk.posedge

        wren.next = True
        data_in.next = 0xAA
        yield clk.posedge
        wren.next = False   
        yield clk.posedge
        assert  fifo_empty

  
        wren.next = True
        data_in.next = 0xA1
        yield clk.posedge
        wren.next = False
        yield clk.posedge
        assert fifo_empty


        wren.next = True
        data_in.next = 0x11 
        yield clk.posedge
        wren.next = False
        yield clk.posedge
           
        wren.next = True
        data_in.next = 0x101
        yield clk.posedge
        wren.next = False
        yield clk.posedge

        for ii in range(64):
            if ii < 28:
                buf_sel.next =  False
                yield clk.posedge
            else:
                buf_sel.next = True
                yield clk.posedge

            wren.next = True
            data_in.next = ii
            yield clk.posedge
            wren.next = False
            yield clk.posedge


        rd_req.next = True
        yield clk.posedge
        assert data_out == 0xAA
        rd_req.next = False

        buf_sel.next = True
        yield clk.posedge

        rd_req.next = True
        yield clk.posedge
        assert data_out == 0xA1
        rd_req.next = False

        buf_sel.next = True
        yield clk.posedge

        rd_req.next = True
        yield clk.posedge
        assert data_out == 0x11
        rd_req.next = False

        buf_sel.next = True
        yield clk.posedge

        rd_req.next = True
        yield clk.posedge
        assert data_out == 0x101
        rd_req.next = False 

        for ii in range(64):
            if ii < 28:
                buf_sel.next =  True
                yield clk.posedge
            else:
                buf_sel.next = False
                yield clk.posedge

            rd_req.next = True
            yield clk.posedge
            assert data_out == ii
            rd_req.next = False

        yield clk.posedge

        assert fifo_empty
        



        raise StopSimulation

    return dut, tbclk, tbstim


def testbench():

    instance = test()
    instance.config_sim(trace = True)
    instance.run_sim()
    verify.simulator='iverilog'
    assert test().verify_convert() == 0

if __name__ == '__main__':
    testbench() 