
from __future__ import absolute_import

import myhdl
from myhdl import Signal, ResetSignal, intbv, always_seq, always

from .opb import OPBBus


def jpegenc_top(
        clock, reset, 
        datain, datain_valid, 
        dataout, dataout_valid
):

    iram_wdata = Signal(intbv(0)[24:0])
    iram_wren = Signal(bool(0))
    ram_byte = Signal(intbv(0)[8:0])
    ram_wren = Signal(bool(0))
    iram_fifo_afull = Signal(bool(0))
    outif_almost_full = Signal(bool(0))
    ram_wraddr = Signal(intbv(0)[24:0])
    frame_size = Signal(intbv(0)[32:0])

    opb = OPBBus(clock, reset)
    
    jpegenc_inst = jpegenc(
        clock, reset, 
        opb.ABus, opb.BE, opb.DBus_in,
        opb.RNW, opb.select, opb.DBus_out, opb.XferAck,
        opb.retry, opb.toutSup, opb.errAck,
        iram_wdata, iram_wren, iram_fifo_afull,
        ram_byte, ram_wren, ram_wraddr, outif_almost_full,
        frame_size
    )
    jpegenc_inst.name = 'jpegenc'

    bytecnt = Signal(intbv(0, min=0, max=4))

    @always_seq(clock.posedge, reset=reset)
    def beh_data_input():
        iram_wren.next = False

        if bytecnt == 3:
            iram_wren.next = True
            bytecnt.next = 0
        elif datain_valid:
            if bytecnt == 2:
                iram_wdata.next[24:16] = datain
                bytecnt.next = 3
            elif bytecnt == 1:
                iram_wdata.next[16:8] = datain
                bytecnt.next = 2
            elif bytecnt == 0:
                iram_wdata.next[8:0] = datain
                bytecnt.next = 1
        
        dataout.next = ram_byte
        dataout_valid.next = ram_wren

        frame_size.next = 1024

    return myhdl.instances()


jpegenc_top.portmap = dict(
    clock=Signal(bool(0)),
    reset=ResetSignal(0, active=1, async=True),
    datain=Signal(intbv(0)[8:0]),
    datain_valid=Signal(bool(0)),
    dataout=Signal(intbv(0)[8:0]),
    dataout_valid=Signal(bool(0))
)


def jpegenc(
        clock, reset, opb_abus, opb_be, opb_dbus_in,
        opb_rnw, opb_select, opb_dbus_out, opb_xferack,
        opb_retry, opb_toutsup, opb_errack,
        iram_wdata, iram_wren, iram_fifo_afull,
        ram_byte, ram_wren, ram_wraddr, outif_almost_full,
        frame_size
):
    
    opb_dbus_out.driven = True
    opb_xferack.driven = True
    opb_retry.driven = True
    opb_toutsup.driven = True
    opb_errack.driven = True

    iram_fifo_afull.driven = True
    ram_byte.driven = True
    ram_wren.driven = True
    ram_wraddr.driven = True
    frame_size.driven = True

    @always(clock.posedge)
    def beh_stub():
        if opb_rnw:
            opb_dbus_out.next = 0

    return beh_stub


jpegenc.verilog_code = """
    JpegEnc
       JPEGENC_BLOCK
       (
        .CLK               ( $clock ),
        .RST               ( $reset ),  
        .OPB_ABus          ( $opb_abus ),
        .OPB_BE            ( $opb_be ),
        .OPB_DBus_in       ( $opb_dbus_in ),
        .OPB_RNW           ( $opb_rnw ),
        .OPB_select        ( $opb_select ),
        .OPB_DBus_out      ( $opb_dbus_out ),
        .OPB_XferAck       ( $opb_xferack ),
        .OPB_retry         ( $opb_retry ),
        .OPB_toutSup       ( $opb_toutsup ),
        .OPB_errAck        ( $opb_errack ),     
    
        .iram_wdata        ( $iram_wdata ),
        .iram_wren         ( $iram_wren ),
        .iram_fifo_afull   ( $iram_fifo_afull ),
        .ram_byte          ( $ram_byte ),
        .ram_wren          ( $ram_wren ),
        .ram_wraddr        ( $ram_wraddr ),
        .outif_almost_full ( $outif_almost_full ),
        .frame_size        ( $frame_size )
    );

"""


def convert():
    portmap = jpegenc_top.portmap
    myhdl.toVerilog(jpegenc_top, **portmap)


if __name__ == '__main__':
    convert()
