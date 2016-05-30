#!/bin/python
from myhdl import StopSimulation, block, Signal, ResetSignal, intbv, delay, instance, always_comb, always_seq
from random import randrange
from rgb2ycbcr import *
from myhdl.conversion import verify

def rgb_to_ycbcr(r, g, b):

    ycbcr = [None for _ in range(3)]
    ycbcr[0] = int(
        round(Y_COEFF[0] *
              float(r) +
              Y_COEFF[1] *
              float(g) +
              Y_COEFF[2] *
              float(b) +
              OFFSET[0]))
    ycbcr[1] = int(
        round(
            CB_COEFF[0] *
            float(r) +
            CB_COEFF[1] *
            float(g) +
            CB_COEFF[2] *
            float(b) +
            OFFSET[1]))
    ycbcr[2] = int(
        round(
            CR_COEFF[0] *
            float(r) +
            CR_COEFF[1] *
            float(g) +
            CR_COEFF[2] *
            float(b) +
            OFFSET[2]))

    return tuple(ycbcr)


@block
def test(samples, num_fractional_bits, pixel_bits, verification):

    ycbcr = YCbCr(pixel_bits)
    rgb = RGB(pixel_bits)

    clock =  Signal(bool(0))
    reset = ResetSignal(1, active=True, async=True)

    rgb2ycbcr_inst = rgb2ycbcr(rgb, ycbcr, clock, reset, num_fractional_bits)

    # create the test input values and the output values
    input_red, input_green, input_blue, output_y, output_cb, output_cr = [
        [] for _ in range(6)]
    for i in range(samples):
        r, g, b = [randrange(256) for _ in range(3)]
        input_red.append(r)
        input_green.append(g)
        input_blue.append(b)
        out = rgb_to_ycbcr(r, g, b)
        output_y.append(out[0])
        output_cb.append(out[1])
        output_cr.append(out[2])

    input_red = tuple(input_red)
    input_green = tuple(input_green)
    input_blue = tuple(input_blue)
    output_y = tuple(output_y)
    output_cb = tuple(output_cb)
    output_cr = tuple(output_cr)

    output_y_s, output_cb_s, output_cr_s = [
        Signal(intbv(0)[pixel_bits:]) for _ in range(3)]

    @instance
    def clkgen():
        clock.next = 0
        while True:
            yield delay(10)
            clock.next = not clock

    @instance
    def resetOnStart():
        reset.next = True
        yield clock.negedge
        reset.next = False

    @instance
    def stimulus():

        print "Fractional Bits: %d"%num_fractional_bits
        print "Pixel Bits: %d"%pixel_bits
        MSE=0

        yield clock.negedge

        rgb.data_valid.next = True

        for i in range(samples):

            yield clock.negedge

            rgb.red.next = input_red[i]
            rgb.green.next = input_green[i]
            rgb.blue.next = input_blue[i]

            if i > 2:

                assert ycbcr.data_valid == True

                output_y_s.next = output_y[i-3]
                output_cb_s.next = output_cb[i-3]
                output_cr_s.next = output_cr[i-3]

                yield delay(1)
                print("Output should be: %d %d %d---Real output is: %d %d %d" % (output_y_s, output_cb_s, output_cr_s,
                                                                                 ycbcr.y, ycbcr.cb, ycbcr.cr))


                #MEAN SQUARED ERROR
                if __debug__:
                    MSE = MSE + (1/float(samples)) * ((output_y_s - ycbcr.y)**2 + (output_cb_s - ycbcr.cb)**2 + (output_cr_s - ycbcr.cr)**2)
                    if (i == samples-1 and not verification):
                        print("Mean Squared Error: %f"% MSE)

                #assert output_y_s == ycbcr.y
                #assert output_cb_s == ycbcr.cb
                #assert output_cr_s == ycbcr.cr

        raise StopSimulation

    return stimulus, resetOnStart, clkgen, rgb2ycbcr_inst


def testbench():

    samples= 50
    fract_bits = 16
    nbits = 8

    instance = test(samples, fract_bits, nbits, verification = False)
    instance.config_sim(trace=False)
    instance.run_sim()

    verify.simulator = 'ghdl'
    assert test(samples, fract_bits, nbits, verification = True).verify_convert() == 0

if __name__ == '__main__':
    testbench()
