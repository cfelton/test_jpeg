#!/bin/python
from myhdl import *
from random import randrange
from commons import *
from rgb2ycbcr import *

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
    input_list=[]
    output_list=[]

    @always(delay(10))
    def clkgen():
        clk.next = not clk

    @instance
    def resetOnStart():
        reset.next = ACTIVE_LOW
        yield clk.negedge
        reset.next = INACTIVE_HIGH

    @instance
    def stimulus():
        yield clk.negedge
        r,g,b=[randrange(256) for _ in range(3)]
        rgb.next(r, g, b)
        input_list.append((r,g,b))
        out=rgb_to_ycbcr(r,g,b)
        output_list.append(out)
        #print "Input:",r,g,b,"Output:",out
        enable_in.next = ACTIVE_HIGH
        #enable_in.next = INACTIVE_LOW if randrange(6) == 0 else ACTIVE_HIGH
        for i in range(50):

            yield clk.negedge
            yield clk.negedge
            r,g,b=[randrange(256) for _ in range(3)]
            rgb.next(r, g, b)
            input_list.append((r,g,b))
            out=rgb_to_ycbcr(r,g,b)
            output_list.append(out)
            yield clk.negedge

            print "Output should be: %s %s %s---Real output is: %d %d %d"%(output_list[i][0],output_list[i][1],output_list[i][2],
                ycbcr.y,ycbcr.cb,ycbcr.cr)

            assert output_list[i][0] == ycbcr.y
            assert output_list[i][1] == ycbcr.cb
            assert output_list[i][2] == ycbcr.cr

        raise StopSimulation

    return stimulus,resetOnStart,clkgen,rgb2ycbcr_inst


def testbench():

   instance=test()
   instance.config_sim(trace=True)
   instance.run_sim()


if __name__ == '__main__':
    testbench()
