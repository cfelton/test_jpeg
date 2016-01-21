#!/bin/python
from myhdl import *
from commons import *
from math import *

from math import *

#Fixed point representation with 1 sign bit and 14 fractional bits
fract_bits = 14
sign_bits=1

Y_COEFF=[0.2999,0.587,0.114]
CB_COEFF=[-0.1687,-0.3313,0.5]
CR_COEFF=[0.5,-0.4187,-0.0813]
OFFSET=[0,128,128]

Y=[int(round(Y_COEFF[i]*(2**fract_bits )))for i in range(3)]
Cb=[int(round(CB_COEFF[i]*(2**fract_bits ))) for i in range(3)]
Cr=[int(round(CR_COEFF[i]*(2**fract_bits ))) for i in range(3)]
Offset=[int(round(OFFSET[i]*(2**fract_bits ))) for i in range(3)]

class RGB(object):

    def __init__(self, nbits=8):
        self.nbits=nbits
        self.red = Signal(intbv(0)[nbits:])
        self.green = Signal(intbv(0)[nbits:])
        self.blue = Signal(intbv(0)[nbits:])

    def next(self, r, g, b):
        self.red.next = r
        self.green.next = g
        self.blue.next = b

    def bitLength(self): return self.nbits


class YCbCr(object):

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.y = Signal(intbv(0)[nbits:])
        self.cb = Signal(intbv(0)[nbits:])
        self.cr = Signal(intbv(0)[nbits:])

    def bitLength(self): return self.nbits


def rgb2ycbcr(ycbcr, enable_out, rgb, enable_in, clk, reset):
    """ A RGB to YCbCr converter with reset.

    I/O pins:
    --------
    y           : output 8-bit unsigned value in range of 0-127
    cb          : output 8-bit unsigned value in range of 0-128
    cr          : output 8-bit unsigned value in range of 0-128
    enable_out  : output True when output is available
    r           : input 8-bit unsigned value in range of 0-255
    g           : input 8-bit unsigned value in range of 0-255
    b           : input 8-bit unsigned value in range of 0-255
    enable_in   : input True when input is available
    clk         : input clock boolean signal
    reset       : input reset boolean signal

    """
    
    #signals for y,cb,cr registers
    Y_reg,Cb_reg,Cr_reg=[[Signal(intbv(0,-2**(23),2**(23)-1)) for _ in range(3)] for _ in range(3)]
    Y_sum,Cb_sum,Cr_sum=[Signal(intbv(0,-2**(23),2**(23)-1)) for _ in range(3)]
    
    #signals for signed input RGB
    R_s,G_s,B_s=[Signal(intbv(0,-2**8,2**8-1)) for _ in range(3)]
    
    #signals for coefficient signed conversion
    Y1_s,Y2_s,Y3_s=[Signal(intbv(Y[i],-2**14,2**14-1)) for i in range(3)]
    Cb1_s,Cb2_s,Cb3_s=[Signal(intbv(Cb[i],-2**14,2**14-1)) for i in range(3)]
    Cr1_s,Cr2_s,Cr3_s=[Signal(intbv(Cr[i],-2**14,2**14-1)) for i in range(3)]
    offset_y,offset_cb,offset_cr=[Signal(intbv(Offset[i],-2**23,2**23-1)) for i in range(3)]
        
    @always_comb
    def logic2():
        #input RGB signed conversion
        R_s.next=rgb.red
        G_s.next=rgb.green
        B_s.next=rgb.blue
        
        
    @always_seq(clk.posedge, reset=reset)
    def logic():
        
        
        enable_out.next = INACTIVE_LOW

        
        
        if enable_in == ACTIVE_HIGH:

           
           Y_reg[0].next=R_s*Y1_s
           Y_reg[1].next=G_s*Y2_s
           Y_reg[2].next=B_s*Y3_s
           

           Cb_reg[0].next=R_s*Cb1_s
           Cb_reg[1].next=G_s*Cb2_s
           Cb_reg[2].next=B_s*Cb3_s
           
           Cr_reg[0].next=R_s*Cr1_s
           Cr_reg[1].next=G_s*Cr2_s
           Cr_reg[2].next=B_s*Cr3_s
           
           
           Y_sum.next=Y_reg[0]+Y_reg[1]+Y_reg[2]+offset_y
           Cb_sum.next=Cb_reg[0]+Cb_reg[1]+Cb_reg[2]+offset_cb
           Cr_sum.next=Cr_reg[0]+Cr_reg[1]+Cr_reg[2]+offset_cr


           #outputs y,cr,cb unsigned 8 MSB
           ycbcr.y.next=Y_sum[22:14]
           ycbcr.cb.next=Cb_sum[22:14]
           ycbcr.cr.next=Cr_sum[22:14]
           
        enable_out.next = ACTIVE_HIGH
    return logic,logic2

def convert():
    ycbcr = YCbCr()
    rgb = RGB()

    clk, enable_in, enable_out = [Signal(INACTIVE_LOW) for _ in range(3)]
    reset = ResetSignal(1, active=ACTIVE_LOW, async=True)
    toVHDL(rgb2ycbcr,ycbcr, enable_out, rgb, enable_in, clk, reset)


convert()





    
