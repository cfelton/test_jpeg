
import myhdl
from myhdl import Signal, ResetSignal, intbv, always, always_seq, enum


@myhdl.block
def fdct_read_proc_sm_monitor(
  clock,           # system clock
  reset,           # system reset

  sof,             # start of frame
  start_int,       # internal restart

  x_pixel_cnt,     # 
  y_line_cnt,      # 
  img_size_x,      #
  img_size_y,      #

  cmp_idx,         # component index
  cur_cmp_idx,     # 

  rd_started,      #
  bf_fifo_hf_full, #

  fram1_rd,        # read data
  fram1_raddr,     # current read address
  fram1_ln_cnt,    #
  fram1_px_cnt,    # 
  fram1_we,        # write new data
  fram1_waddr,     # write address

  midv,            # MDCT input data valid
  modv,            # MDCT output data valid

  zz_rd,           # zigzag read
  zz_raddr,        # zigzag read-address
):
    """
    This monitors the signals from the FDCT and tries to indentifiy
    a state that should correspond to the ...  
    """

    States = enum('Idle', 'Process', 'Stall')
    state = Signal(States.Idle)

    MemSize = 2**(len(fram1_waddr))
    wcnt = [Signal(intbv(0)[32:]) for _ in range(MemSize)]
    rcnt = [Signal(intbv(0)[32:]) for _ in range(MemSize)]

    # FDCT input and output counters
    ipcnt = Signal(intbv(0)[32:])
    iccnt = Signal(intbv(0)[32:])
    ircnt = Signal(intbv(0)[32:])

    opcnt = Signal(intbv(0)[32:])
    occnt = Signal(intbv(0)[32:])
    orcnt = Signal(intbv(0)[32:])

    # MDCT input and output counters
    mi_pcnt = Signal(intbv(0)[32:])
    mi_ccnt = Signal(intbv(0)[32:])
    mi_rcnt = Signal(intbv(0)[32:])

    mo_pcnt = Signal(intbv(0)[32:])
    mo_ccnt = Signal(intbv(0)[32:])
    mo_rcnt = Signal(intbv(0)[32:])


    @always(clock.posedge)
    def monmem():
        if fram1_rd:
            rcnt[fram1_raddr].next = rcnt[fram1_raddr] + 1

        if fram1_we:
            wcnt[fram1_waddr].next = wcnt[fram1_waddr] + 1

        for ii in range(MemSize):
            if not (rcnt[ii] >= (wcnt[ii] + 4)):
                print("%d: rcnt %d, wcnt %d" % (ii, rcnt[ii], wcnt[ii],))


    @always_seq(clock.posedge, reset=reset)
    def moncnt():
        if fram1_we:
            ipcnt.next = ipcnt + 1
            
            if iccnt < (img_size_x-1):
                iccnt.next = iccnt + 1
            else:
                iccnt.next = 0
                if ircnt < (img_size_y-1):
                    ircnt.next = ircnt + 1
                else:
                    ircnt.next = 0

            if (ircnt+1 == 80 and iccnt+1 == 80):
                print("II: %d, %dx%d" % (ipcnt+1, ircnt+1, iccnt+1))
        
        if zz_rd:
            opcnt.next = opcnt + 1
            
            if occnt < ((4*img_size_x)-1):
                occnt.next = occnt + 1
            else:
                occnt.next = 0
                if orcnt < (img_size_y-1):
                    orcnt.next = orcnt + 1
                else:
                    orcnt.next = 0

            # assuming subsampling 2
            if (orcnt+1 == 40 and occnt+1 == (40*4)):
                print("OO: %d, %dx%d" % (opcnt+1, orcnt+1, occnt+1))


        if midv:
            mi_pcnt.next = mi_pcnt + 1
            
            if mi_ccnt < ((4*img_size_x)-1):
                mi_ccnt.next = mi_ccnt + 1
            else:
                mi_ccnt.next = 0
                if mi_rcnt < (img_size_y-1):
                    mi_rcnt.next = mi_rcnt + 1
                    #print("MI: %d, %dx%d" % (mi_pcnt+1, mi_rcnt+1, mi_ccnt+1))
                else:
                    mi_rcnt.next = 0


        if modv:
            mo_pcnt.next = mo_pcnt + 1
            
            if mo_ccnt < ((4*img_size_x)-1):
                mo_ccnt.next = mo_ccnt + 1
            else:
                mo_ccnt.next = 0
                if mo_rcnt < (img_size_y-1):
                    mo_rcnt.next = mo_rcnt + 1
                    #print("MO: %d, %dx%d" % (mo_pcnt+1, mo_rcnt+1, mo_ccnt+1))
                else:
                    mo_rcnt.next = 0



    # need to verify the number in equals the number out!
    @always_seq(clock.posedge, reset=reset)
    def mon():

        if state == States.Idle:
            if sof or start_int:
                #print("%d: %d, %d - cmp %d ccmp %d - sof %d si %d" % \
                #      (now(), x_pixel_cnt, y_line_cnt, cmp_idx, cur_cmp_idx,
                #       sof, start_int))
                pass
            state.next = States.Idle

        elif state == States.Process:
            state.next = States.Idle

        elif state == States.Stall:
            state.next = States.Idle

        else:
            print("invalid state %s" % (state,))
            state.next = States.Idle

    return mon, monmem, moncnt


def convert():
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    sof = Signal(bool(0))
    start_int = Signal(bool(0))
    
    x_pixel_cnt = Signal(intbv(0, min=0, max=60000))
    y_line_cnt  = Signal(intbv(0, min=0, max=60000))
    img_size_x  = Signal(intbv(0, min=0, max=60000))
    img_size_y  = Signal(intbv(0, min=0, max=60000))

    cmp_idx     = Signal(intbv(0, min=0, max=8))
    cur_cmp_idx = Signal(intbv(0, min=0, max=8))
    rd_started  = Signal(bool(0))

    bf_fifo_hf_full = Signal(bool(0))

    fram1_rd       = Signal(bool(0))     
    fram1_raddr    = Signal(intbv(0)[7:])
    fram1_ln_cnt   = Signal(intbv(0)[3:])
    fram1_px_cnt   = Signal(intbv(0)[3:])
    fram1_we       = Signal(bool(0))     
    fram1_waddr    = Signal(intbv(0)[7:])

    midv           = Signal(bool(0))
    modv           = Signal(bool(0))

    zz_rd          = Signal(bool(0))
    zz_raddr       = Signal(intbv(0)[6:])


    inst = fdct_read_proc_sm_monitor(
        clock, reset, sof, start_int, x_pixel_cnt, y_line_cnt,
        img_size_x, img_size_y, cmp_idx, cur_cmp_idx,
        rd_started, bf_fifo_hf_full, fram1_rd, fram1_raddr,
        fram1_ln_cnt, fram1_px_cnt, fram1_we, fram1_waddr,
        midv, modv, zz_rd, zz_raddr
    )

    inst.convert(hdl='Verilog', directory='output_files', testbench=False)

if __name__ == '__main__':
    convert()