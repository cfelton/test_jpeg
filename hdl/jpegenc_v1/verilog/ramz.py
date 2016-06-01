
import myhdl
from myhdl import Signal, intbv, always_comb, always

@myhdl.block
def ramz(d, waddr, raddr, we, clk, q):
    """
    default addr width 6, data width 12
    """
    mem_size = 2**len(waddr)
    mem = [Signal(intbv(0)[len(d):]) for _ in range(mem_size)]

    read_addr = Signal(raddr)

    @always_comb
    def beh_out():
        q.next = mem[read_addr];

    @always(clk.posedge)
    def beh_write():
        read_addr.next = raddr

        if we:
            mem[waddr].next = d

    return beh_out, beh_write


def convert():
    clock = Signal(bool(0))
    we = Signal(bool(0))
    waddr = Signal(intbv(0)[6:])
    raddr = Signal(intbv(0)[6:])
    d = Signal(intbv(0)[12:])
    q = Signal(intbv(0)[12:])

    inst = ramz(d, waddr, raddr, we, clock, q)
    inst.convert(hdl='Verilog', name='RAM_6x12',
                 directory='output_files', testbench=False)

    # RAM module is the same but with 
    # addr = 6, data == 10
    d = Signal(intbv(0)[10:])
    q = Signal(intbv(0)[10:])
    inst = ramz(d, waddr, raddr, we, clock, q)
    inst.convert(hdl='Verilog', name='RAM',
                 directory='output_files', testbench=False)


if __name__ == '__main__':
    convert()
           