#!/bin/python
from myhdl import *
from random import randrange
from commons import *
from rgb2ycbcr import *
from myhdl.conversion import *

def rgb_to_ycbcr(r,g,b):

    ycbcr=[None for _ in range(3)]
    ycbcr[0]=int(round(Y_COEFF[0]*float(r)+Y_COEFF[1]*float(g)+Y_COEFF[2]*float(b)+OFFSET[0]))
    ycbcr[1]=int(round(CB_COEFF[0]*float(r)+CB_COEFF[1]*float(g)+CB_COEFF[2]*float(b)+OFFSET[1]))
    ycbcr[2]=int(round(CR_COEFF[0]*float(r)+CR_COEFF[1]*float(g)+CR_COEFF[2]*float(b)+OFFSET[2]))

    return tuple(ycbcr)

@block
def test():

    ycbcr = YCbCr()
    rgb = RGB()

    clk, enable_in, enable_out = [Signal(INACTIVE_LOW) for _ in range(3)]
    reset = ResetSignal(1, active=ACTIVE_LOW, async=True)

    rgb2ycbcr_inst = rgb2ycbcr(ycbcr, enable_out, rgb, enable_in, clk, reset)

    #create the test input values and the output values
    input_red,input_green,input_blue,output_y,output_cb,output_cr=[[] for _ in range(6)]
    samples=50
    for i in range(samples):
        r,g,b=[randrange(256) for _ in range(3)]
        input_red.append(r)
        input_green.append(g)
        input_blue.append(b)
        out=rgb_to_ycbcr(r,g,b)
        output_y.append(out[0])
        output_cb.append(out[1])
        output_cr.append(out[2])

    input_red=tuple(input_red)
    input_green=tuple(input_green)
    input_blue=tuple(input_blue)
    output_y=tuple(output_y)
    output_cb=tuple(output_cb)
    output_cr=tuple(output_cr)


    output_y_s,output_cb_s,output_cr_s=[Signal(intbv(0)[nbits:]) for _ in range(3)]

    @instance
    def clkgen():
        clk.next=0
        while True:
            yield delay(10)
            clk.next = not clk


    @instance
    def resetOnStart():
        reset.next = ACTIVE_LOW
        yield clk.negedge
        reset.next = INACTIVE_HIGH

    @instance
    def stimulus():
        yield clk.negedge

        #rgb.next(input_list[0][0], input_list[0][1], input_list[0][2])
        rgb.red.next=input_red[0]
        rgb.green.next=input_green[0]
        rgb.blue.next=input_blue[0]

        enable_in.next = ACTIVE_HIGH

        #enable_in.next = INACTIVE_LOW if randrange(6) == 0 else ACTIVE_HIGH
        for i in range(1,samples):
            yield clk.negedge
            yield clk.negedge

            rgb.red.next=input_red[i]
            rgb.green.next=input_green[i]
            rgb.blue.next=input_blue[i]
            yield clk.negedge


            output_y_s.next=output_y[i-1]
            output_cb_s.next=output_cb[i-1]
            output_cr_s.next=output_cr[i-1]

            yield delay(1)
            print "Output should be: %d %d %d---Real output is: %d %d %d"%(output_y_s,output_cb_s,output_cr_s,
                ycbcr.y,ycbcr.cb,ycbcr.cr)

            assert output_y_s== ycbcr.y
            assert output_cb_s== ycbcr.cb
            assert output_cr_s== ycbcr.cr

        raise StopSimulation

    return stimulus,resetOnStart,clkgen,rgb2ycbcr_inst


def testbench():

   instance=test()
   instance.config_sim(trace=False)
   instance.run_sim()

   verify.simulator='iverilog'
   assert test().verify_convert() == 0

if __name__ == '__main__':
    testbench()
