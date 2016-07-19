"""This ram is used to store quantization values"""


import myhdl
from myhdl import Signal, intbv, always_comb, always


@myhdl.block
def ramz(data_in, waddr, raddr, write_enable, clk, data_out):
    """
    default addr width 6, data width 12
    """
    mem_size = 2**(len(waddr))
    mem = [Signal(intbv(0)[len(data_in):].signed()) for _ in range(mem_size)]

    read_addr = Signal(raddr.val)

    @always_comb
    def beh_out():
        """write values to output pin"""
        data_out.next = mem[read_addr]

    @always(clk.posedge)
    def beh_write():
        """read values from the input pin"""
        read_addr.next = raddr

        if write_enable:
            mem[waddr].next = data_in

    return beh_out, beh_write
