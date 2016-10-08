
import os

# the directory with the reference design Verilg/VHDL
refdir = './reference_designs/'

# Version 1 JPEG encoder
filelist_v1 = [
    'jpegenc_v1/verilog/AC_CR_ROM.v',
    'jpegenc_v1/verilog/AC_ROM.v',
    'jpegenc_v1/verilog/DC_ROM.v',
    'jpegenc_v1/verilog/DC_CR_ROM.v',
    'jpegenc_v1/verilog/BUF_FIFO.v',
    'jpegenc_v1/verilog/ByteStuffer.v',
    'jpegenc_v1/verilog/OutMux.v',
    'jpegenc_v1/verilog/CtrlSM.v',
    'jpegenc_v1/verilog/DBUFCTL.v',
    'jpegenc_v1/verilog/RAM.v',
    'jpegenc_v1/verilog/RAMZ.v',
    'jpegenc_v1/verilog/ROMR.v',
    'jpegenc_v1/verilog/SUB_RAMZ.v',
    'jpegenc_v1/verilog/RAMF.v',
    'jpegenc_v1/verilog/FIFO.v',
    'jpegenc_v1/verilog/SingleSM.v',
    'jpegenc_v1/verilog/r_divider.v',
    'jpegenc_v1/verilog/ROMO.v',
    'jpegenc_v1/verilog/ROME.v',
    'jpegenc_v1/verilog/HeaderRAM.v',
    'jpegenc_v1/verilog/DoubleFifo.v',
    'jpegenc_v1/verilog/RleDoubleFifo.v',
    'jpegenc_v1/verilog/RLE.v',
    'jpegenc_v1/verilog/RLE_TOP.v',
    'jpegenc_v1/verilog/DCT1D.v',
    'jpegenc_v1/verilog/DCT2D.v',
    'jpegenc_v1/verilog/m_fdct_read_proc_sm_monitor.v',
    'jpegenc_v1/verilog/FDCT.v',
    'jpegenc_v1/verilog/HostIF.v',
    'jpegenc_v1/verilog/Huffman.v',
    'jpegenc_v1/verilog/QUANTIZER.v',
    'jpegenc_v1/verilog/MDCT.v',
    'jpegenc_v1/verilog/m_zz_rom.v',
    'jpegenc_v1/verilog/ZIGZAG.v',
    'jpegenc_v1/verilog/JFIFGen.v',
    'jpegenc_v1/verilog/QUANT_TOP.v',
    'jpegenc_v1/verilog/ZZ_TOP.v',
    'jpegenc_v1/verilog/JpegEnc.v'

]

# Version 2 JPEG encoder
filelist_v2 = [
    'jpegenc_v2/verilog/cb_dct.v       ',     
    'jpegenc_v2/verilog/cb_huff.v      ',
    'jpegenc_v2/verilog/cb_quantizer.v ',
    'jpegenc_v2/verilog/cbd_q_h.v      ',
    'jpegenc_v2/verilog/cr_dct.v       ',
    'jpegenc_v2/verilog/cr_huff.v      ',
    'jpegenc_v2/verilog/cr_quantizer.v ',
    'jpegenc_v2/verilog/crd_q_h.v      ',
    'jpegenc_v2/verilog/ff_checker.v   ',
    'jpegenc_v2/verilog/fifo_out.v     ',
    'jpegenc_v2/verilog/jpeg_top.v     ',
    'jpegenc_v2/verilog/pre_fifo.v     ',
    'jpegenc_v2/verilog/rgb2ycbcr.v    ',
    'jpegenc_v2/verilog/sync_fifo_32.v ',
    'jpegenc_v2/verilog/sync_fifo_ff.v ',
    'jpegenc_v2/verilog/y_dct.v        ',
    'jpegenc_v2/verilog/y_huff.v       ',
    'jpegenc_v2/verilog/y_quantizer.v  ',
    'jpegenc_v2/verilog/yd_q_h.v       ', 
]

for ii, fn in enumerate(filelist_v1):
    filelist_v1[ii] = os.path.join(refdir, fn)

for ii, fn in enumerate(filelist_v2):
    filelist_v2[ii] = os.path.join(refdir, fn)
