from myhdl import *
from Fifo import *
from fifobus import *
from myhdl.conversion import *

@block
def rledoublefifo(clk, reset, data_in, wren, buf_sel, rd_req, fifo_empty, data_out):

    fifo_data_in = Signal(intbv(0)[20:])

    fbus1 = FIFOBus(width = 20, size = 64)
    fbus2 = FIFOBus(width = 20, size = 64)


    fifo_sync1 = fifo_sync(clk, reset, fbus1)
    fifo_sync2 = fifo_sync(clk, reset, fbus2)


    
    @always_comb
    def initial():
        fbus1.write_data.next = fifo_data_in
        fbus2.write_data.next = fifo_data_in


    @always_seq(clk.posedge, reset = reset)
    def mux2_logic():
        if buf_sel == 0:
            fbus1.write.next = wren
        else:
            fbus2.write.next = wren
            
        fifo_data_in.next = data_in


    @always_comb
    def initial2():
        fbus1.read.next = rd_req if buf_sel == 1 else 0
        fbus2.read.next = rd_req if buf_sel == 0 else 0
        data_out.next = fbus1.read_data if buf_sel == 1 else fbus2.read_data
        fifo_empty.next = fbus1.empty if buf_sel == 1 else fbus2.empty


    return fifo_sync1, fifo_sync2, initial, mux2_logic, initial2


def convert():

    clk = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)
    data_in = Signal(intbv(0)[20:])
    wren = Signal(bool(0))
    buf_sel = Signal(bool(0))
    rd_req = Signal(bool(0))
    fifo_empty = Signal(bool(0))
    data_out = Signal(intbv()[20:])
    dut = rledoublefifo(clk, reset, data_in, wren, buf_sel, rd_req, fifo_empty, data_out)

    analyze.simulator = 'iverilog'
    assert rledoublefifo(clk, reset, data_in, wren, buf_sel, rd_req, fifo_empty, data_out).analyze_convert() == 0

if __name__ == '__main__':
    convert()