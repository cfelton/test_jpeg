#!/bin/python
from myhdl import block, Signal, ResetSignal, intbv, delay, instance, always_comb, always_seq
from myhdl.conversion import analyze


#Fixed point representation with 1 sign bit and 14 fractional bits
fract_bits=14
nbits=8

a=fract_bits + nbits
b=fract_bits


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

    def bitLength(self): return self.nbits


class YCbCr(object):

    def __init__(self, nbits=8):
        self.nbits = nbits
        self.y = Signal(intbv(0)[nbits:])
        self.cb = Signal(intbv(0)[nbits:])
        self.cr = Signal(intbv(0)[nbits:])

    def bitLength(self): return self.nbits

@block
def rgb2ycbcr(ycbcr, enable_out, rgb, enable_in, clk, reset):


    #Ranges for multiplication and addition signals
    #to find the bit width required for a multiplication: 2*fract_bits + 2*sign_bits + 2*sign_bits
    mult_max_range=2**(nbits+fract_bits+1)
    rgb_range=2**nbits
    coeff_range=2**fract_bits

    #signals for y,cb,cr registers
    Y_reg,Cb_reg,Cr_reg=[[Signal(intbv(0,min=-mult_max_range,max=mult_max_range)) for _ in range(3)] for _ in range(3)]
    Y_sum,Cb_sum,Cr_sum=[Signal(intbv(0,min=-mult_max_range,max=mult_max_range)) for _ in range(3)]

    #signals for signed input RGB
    R_s,G_s,B_s=[Signal(intbv(0,min=-rgb_range,max=rgb_range)) for i in range(3)]

    #signals for coefficient signed conversion
    Y1_s,Y2_s,Y3_s=[Signal(intbv(Y[i],min=-coeff_range,max=coeff_range)) for i in range(3)]
    Cb1_s,Cb2_s,Cb3_s=[Signal(intbv(Cb[i],min=-coeff_range,max=coeff_range)) for i in range(3)]
    Cr1_s,Cr2_s,Cr3_s=[Signal(intbv(Cr[i],min=-coeff_range,max=coeff_range)) for i in range(3)]
    offset_y,offset_cb,offset_cr=[Signal(intbv(Offset[i],min=-mult_max_range,max=mult_max_range)) for i in range(3)]

    enable_out_reg=[Signal(bool(0)) for _ in range(2)]

    @always_comb
    def logic2():
        #input RGB signed conversion
        R_s.next=rgb.red
        G_s.next=rgb.green
        B_s.next=rgb.blue


    @always_seq(clk.posedge, reset=reset)
    def logic():


        if enable_in == 1:


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

           #rounding

           """
           the part which must be checked for rounding is the part from signal[fract_bits + nbits:fract_bits]
           """


           if(Y_sum[b - 1]==1 and Y_sum[a:b]!=(2**nbits)):
              ycbcr.y.next=Y_sum[a:b]+1
           else:
              ycbcr.y.next=Y_sum[a:b]
           if(Cb_sum[b- 1]==1 and Cb_sum[a:b]!=(2**nbits)):
                 ycbcr.cb.next=Cb_sum[a:b]+1
           else:
                 ycbcr.cb.next=Cb_sum[a:b]
           if(Cr_sum[b- 1]==1 and Cr_sum[a:b]!=(2**nbits)):
                    ycbcr.cr.next=Cr_sum[a:b]+1
           else:
                    ycbcr.cr.next=Cr_sum[a:b]

           #enable_out delayed
           enable_out_reg[0].next=enable_in
           enable_out_reg[1].next=enable_out_reg[0]
           enable_out.next = enable_out_reg[1]

        else:

            enable_out.next = 0

    return logic,logic2


def convert():
    ycbcr = YCbCr()
    rgb = RGB()

    clk, enable_in, enable_out = [Signal(bool(0)) for _ in range(3)]
    reset = ResetSignal(1, active=1, async=True)
    #instance=rgb2ycbcr(ycbcr, enable_out, rgb, enable_in, clk, reset)
    #instance.convert(hdl='VHDL')


    analyze.simulator= 'ghdl'
    assert rgb2ycbcr(ycbcr, enable_out, rgb, enable_in, clk, reset).analyze_convert() == 0

if __name__ == '__main__':
    convert()






