
clean :
	$(MAKE) -C work clean
run :
	$(MAKE) -C work run

#compile : $(files)
#	ghdl -a --workdir=work $(files)

compile:
	ghdl -a --workdir=work ../JPEG_PKG.vhd
	ghdl -a --workdir=work ../RAMZ.vhd
	ghdl -a --workdir=work ../FIFO.vhd
	ghdl -a --workdir=work ../SingleSM.vhd
	ghdl -a --workdir=work vhdl/DCT_TROM.vhd

## buffifo
	ghdl -a --workdir=work ../SUB_RAMZ.vhd
#	ghdl -a --workdir=work ../SUB_FIFO.vhd
	ghdl -a --workdir=work ../BUF_FIFO.vhd

## fdct
	ghdl -a --workdir=work ../MDCT_PKG.vhd
	ghdl -a --workdir=work ../ROMO.vhd
	ghdl -a --workdir=work ../ROME.vhd
	ghdl -a --workdir=work ../RAM.vhd
	ghdl -a --workdir=work ../DBUFCTL.vhd
	ghdl -a --workdir=work ../DCT1D.vhd
	ghdl -a --workdir=work ../DCT2D.vhd
	ghdl -a --workdir=work ../MDCT.vhd
	ghdl -a --workdir=work ../FDCT.vhd

##test
	ghdl -a --workdir=work vhdl/DCT_TROM.vhd

## quantizer
##vcom ../design/quantizer/ROMQ.vhd
##vcom ../design/quantizer/s_divider.vhd
	ghdl -a --workdir=work  ../ROMR.vhd
	ghdl -a --workdir=work  ../r_divider.vhd
	ghdl -a --workdir=work  ../QUANTIZER.vhd
	ghdl -a --workdir=work  ../QUANT_TOP.vhd

## zigzag
	ghdl -a --workdir=work  ../ZIGZAG.vhd
	ghdl -a --workdir=work  ../ZZ_TOP.vhd

## rle
	ghdl -a --workdir=work  ../RleDoubleFifo.vhd
	ghdl -a --workdir=work  ../RLE.vhd
	ghdl -a --workdir=work  ../RLE_TOP.vhd

## huffman
	ghdl -a --workdir=work ../DoubleFifo.vhd
	ghdl -a --workdir=work ../DC_ROM.vhd
	ghdl -a --workdir=work ../AC_ROM.vhd
	ghdl -a --workdir=work ../DC_CR_ROM.vhd
	ghdl -a --workdir=work ../AC_CR_ROM.vhd
	ghdl -a --workdir=work ../Huffman.vhd

## bytestuffer
	ghdl -a --workdir=work ../ByteStuffer.vhd

## control
	ghdl -a --workdir=work ../CtrlSM.vhd

## HostIF
	ghdl -a --workdir=work ../HostIF.vhd

## IRamIF
#	ghdl -a --workdir=work ../IRAMIF.vhd

## jfifgen
	ghdl -a --workdir=work ../pck_myhdl_09.vhd
	ghdl -a --workdir=work ../HeaderRam.vhd
	ghdl -a --workdir=work ../JFIFGen.vhd

## outmux
	ghdl -a --workdir=work ../OutMux.vhd

## top
	ghdl -a --workdir=work ../JpegEnc.vhd

## testbench
	ghdl -a --workdir=work vhdl/RAMSIM.vhd
	ghdl -a --workdir=work vhdl/MDCTTB_PKG.vhd
	ghdl -a --workdir=work --ieee=synopsys vhdl/GPL_V2_Image_pkg.vhd
	ghdl -a --workdir=work vhdl/ClkGen.vhd
	ghdl -a --workdir=work --ieee=synopsys vhdl/HostBFM.vhd
	ghdl -a --workdir=work --ieee=synopsys --vcd=debug.vcd vhdl/JPEG_TB.vhd
