
import myhdl
from myhdl import Signal, intbv, always
from mdct import coe


@myhdl.block
def romo(addr, clk, datao):

    # this was copied from the MDCT_PKG and ROMO component,
    # need to determine the algorithm.  The comments suggest
    # it is the precomputed MAC (which MAC?).
    
    rom_size = 2**len(addr)
    rom = [0 for _ in range(rom_size)]

    # what is the pattern here - there is one ...
    # ??
    rom[0]  = 0
    rom[1]  = coe['GP']
    rom[2]  = coe['FP']
    rom[3]  = coe['FP'] + coe['GP']
    rom[4]  = coe['EP']
    rom[5]  = coe['EP'] + coe['GP']
    rom[6]  = coe['EP'] + coe['FP']
    rom[7]  = coe['EP'] + coe['FP'] + coe['GP']
    rom[8]  = coe['DP']
    rom[9]  = coe['DP'] + coe['GP']
    rom[10] = coe['DP'] + coe['FP']
    rom[11] = coe['DP'] + coe['FP'] + coe['GP']
    rom[12] = coe['DP'] + coe['EP']    
    rom[13] = coe['DP'] + coe['EP'] + coe['GP']
    rom[14] = coe['DP'] + coe['EP'] + coe['FP']
    rom[15] = coe['DP'] + coe['EP'] + coe['FP'] + coe['GP']

    # ??
    rom[16] = 0
    rom[17] = coe['FM']
    rom[18] = coe['DM']
    rom[19] = coe['DM'] + coe['FM']
    rom[20] = coe['GM']
    rom[21] = coe['GM'] + coe['FM']
    rom[22] = coe['GM'] + coe['DM']
    rom[23] = coe['GM'] + coe['DM'] + coe['FM']
    rom[24] = coe['EP']
    rom[25] = coe['EP'] + coe['FM']
    rom[26] = coe['EP'] + coe['DM']
    rom[27] = coe['EP'] + coe['DM'] + coe['FM']
    rom[28] = coe['EP'] + coe['GM']    
    rom[29] = coe['EP'] + coe['GM'] + coe['FM']
    rom[30] = coe['EP'] + coe['GM'] + coe['DM']
    rom[31] = coe['EP'] + coe['GM'] + coe['DM'] + coe['FM']

    # ??
    rom[32] = 0
    rom[33] = coe['EP']
    rom[34] = coe['GP']
    rom[35] = coe['EP'] + coe['GP']
    rom[36] = coe['DM']
    rom[37] = coe['DM'] + coe['EP']
    rom[38] = coe['DM'] + coe['GP']
    rom[39] = coe['DM'] + coe['GP'] + coe['EP']
    rom[40] = coe['FP']
    rom[41] = coe['FP'] + coe['EP']
    rom[42] = coe['FP'] + coe['GP']
    rom[43] = coe['FP'] + coe['GP'] + coe['EP']
    rom[44] = coe['FP'] + coe['DM']    
    rom[45] = coe['FP'] + coe['DM'] + coe['EP']
    rom[46] = coe['FP'] + coe['DM'] + coe['GP']
    rom[47] = coe['FP'] + coe['DM'] + coe['GP'] + coe['EP']

    # ??
    rom[48] = 0
    rom[49] = coe['DM']
    rom[50] = coe['EP']
    rom[51] = coe['EP'] + coe['DM']
    rom[52] = coe['FM']
    rom[53] = coe['FM'] + coe['DM']
    rom[54] = coe['FM'] + coe['DP']
    rom[55] = coe['FM'] + coe['EP'] + coe['DM']
    rom[56] = coe['GP']
    rom[57] = coe['GP'] + coe['DM']
    rom[58] = coe['GP'] + coe['EP']
    rom[59] = coe['GP'] + coe['EP'] + coe['DM']
    rom[60] = coe['GP'] + coe['FM']    
    rom[61] = coe['GP'] + coe['FM'] + coe['DM']
    rom[62] = coe['GP'] + coe['FM'] + coe['EP']
    rom[63] = coe['GP'] + coe['FM'] + coe['EP'] + coe['DM']    

    rom = tuple(rom)

    @always(clk.posedge)
    def beh_output_assign():
        datao.next = rom[addr]

    return beh_output_assign


def convert():
    clock = Signal(bool(0))
    addr = Signal(intbv(0)[6:])
    datao = Signal(intbv(0)[14:])
    inst = romo(addr, clock, datao)
    inst.convert(hdl='Verilog', name='ROMO',
                 directory='output_files', testbench=False)

if __name__ == '__main__':
    convert()