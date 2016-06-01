

import myhdl
from myhdl import Signal, intbv, always
from mdct_coefs import coe


@myhdl.block
def rome(addr, clk, datao):


    rom_size = 2**len(addr)
    rom = [0 for _ in range(rom_size)]

    # ??
    rom[0]  = 0
    rom[1]  = coe['AP']
    rom[2]  = coe['AP']
    rom[3]  = coe['AP'] + coe['AP']
    rom[4]  = coe['AP']
    rom[5]  = coe['AP'] + coe['AP']
    rom[6]  = coe['AP'] + coe['AP']
    rom[7]  = coe['AP'] + coe['AP'] + coe['AP']
    rom[8]  = coe['AP']
    rom[9]  = coe['AP'] + coe['AP']
    rom[10] = coe['AP'] + coe['AP']
    rom[11] = coe['AP'] + coe['AP'] + coe['AP']
    rom[12] = coe['AP'] + coe['AP']    
    rom[13] = coe['AP'] + coe['AP'] + coe['AP']
    rom[14] = coe['AP'] + coe['AP'] + coe['AP']
    rom[15] = coe['AP'] + coe['AP'] + coe['AP'] + coe['AP']

    # ??
    rom[16] = 0
    rom[17] = coe['BM']
    rom[18] = coe['CM']
    rom[19] = coe['CM'] + coe['BM']
    rom[20] = coe['CP']
    rom[21] = coe['CP'] + coe['BM']
    rom[22] = 0
    rom[23] = coe['BM']
    rom[24] = coe['BP']
    rom[25] = 0
    rom[26] = coe['CP'] + coe['CM']
    rom[27] = coe['CM'] 
    rom[28] = coe['BP'] + coe['CP']    
    rom[29] = coe['CP'] 
    rom[30] = coe['BP']
    rom[31] = 0

    # ??
    rom[32] = 0
    rom[33] = coe['AP']
    rom[34] = coe['AM']
    rom[35] = 0
    rom[36] = coe['AM']
    rom[37] = 0
    rom[38] = coe['AM'] + coe['AM']
    rom[39] = coe['AM']
    rom[40] = coe['AP']
    rom[41] = coe['AP'] + coe['AP']
    rom[42] = 0
    rom[43] = coe['AP']
    rom[44] = 0
    rom[45] = coe['AP']
    rom[46] = coe['AM']
    rom[47] = 0

    # ??
    rom[48] = 0
    rom[49] = coe['CM']
    rom[50] = coe['BP']
    rom[51] = coe['BP'] + coe['CM']
    rom[52] = coe['BM']
    rom[53] = coe['BM'] + coe['CM']
    rom[54] = 0
    rom[55] = coe['CM']
    rom[56] = coe['CP']
    rom[57] = 0
    rom[58] = coe['CP'] + coe['BP']
    rom[59] = coe['BP']
    rom[60] = coe['CP'] + coe['BM']    
    rom[61] = coe['BM']
    rom[62] = coe['CP'] + coe['FM'] + coe['EP']
    rom[63] = 0

    rom = tuple(rom)

    @always(clk.posedge)
    def beh_output_assign():
        datao.next = rom[addr]

    return beh_output_assign


def convert():
    clock = Signal(bool(0))
    addr = Signal(intbv(0)[6:])
    datao = Signal(intbv(0)[14:])
    inst = rome(addr, clock, datao)
    inst.convert(hdl='Verilog', name='ROME', 
                 directory='output_files', testbench=False)


if __name__ == '__main__':
    convert()