""" core of the run length encoder module """
from myhdl import always_comb, always_seq, block
from myhdl import intbv, ResetSignal, Signal
from myhdl.conversion import analyze
from jpegenc.subblocks.RLE.RLECore.entropycoder import entropycoder


class Pixel(object):
    def __init__(self):
        self.Y1 = 0
        self.Y2 = 1
        self.Cb = 2
        self.Cr = 3

class DataStream(object):
    """ Input data streams into Rle Core """
    def __init__(self, width):
        self.start = Signal(bool(0))
        self.input_val = Signal(intbv(0)[width:].signed())

class RLESymbols(object):
    """ RLE symbols generatred by RLE Core """
    def __init__(self, width, size, rlength):
        self.runlength = Signal(intbv(0)[rlength:])
        self.size = Signal(intbv(0)[size:])
        self.amplitude = Signal(intbv(0)[width:].signed())
        self.dovalid = Signal(bool(0))

class RLEConfig(object):
    """ RLE configuration Signals are added here """
    def __init__(self, width_rd):
        self.color_component = Signal(intbv(0)[3:])
        self.read_addr = Signal(intbv(0)[width_rd:])
        self.sof = Signal(bool(0))

def sub(num1, num2):
    """subtractor for Difference Encoder"""
    return num1 - num2

pixel = Pixel()

@block
def rle(constants, reset, clock, datastream, rlesymbols, rleconfig):
    """ Input and start Signal send using datastream
        and rle symbols are captured
    """
    rlesymbols_temp = RLESymbols(
        constants.width_data, constants.size, constants.rlength)

    limit = int((2**constants.rlength) - 1)

    prev_dc_0, prev_dc_1, prev_dc_2, zrl_data_in = [Signal(intbv(0)[
        (constants.width_data):].signed()) for _ in range(4)]

    accumulator = Signal(intbv(0)[(constants.width_data + 1):].signed())

    read_en, divalid, divalid_en, zrl_processing = [
        Signal(bool(0)) for _ in range(4)]

    zero_cnt, read_cnt = [Signal(intbv(0)[(constants.max_write_cnt + 1):]) for _ in range(2)]

    write_cnt = Signal(intbv(0)[(constants.max_write_cnt + 1):])

    @always_comb
    def assign():
        """assign size amplitude and read address"""
        rlesymbols.size.next = rlesymbols_temp.size
        rlesymbols.amplitude.next = rlesymbols_temp.amplitude
        rleconfig.read_addr.next = read_cnt


    @always_seq(clock.posedge, reset=reset)
    def mainprocessing():
        """sequential block to calculate the runlength"""
        rlesymbols_temp.dovalid.next = 0
        rlesymbols_temp.runlength.next = 0
        rlesymbols.runlength.next = rlesymbols_temp.runlength
        rlesymbols.dovalid.next = rlesymbols_temp.dovalid
        divalid.next = read_en

        # when start asserts divalid asserts
        if datastream.start:
            read_cnt.next = 0
            read_en.next = True
            divalid_en.next = True

        # after processing the last pixel
        if divalid and write_cnt == constants.max_write_cnt:
            divalid_en.next = False

        if read_en:
            if read_cnt == constants.max_write_cnt:
                read_cnt.next = 0
                read_en.next = False
            else:
                read_cnt.next = read_cnt + 1

        if divalid:
            write_cnt.next = write_cnt + 1

            if write_cnt == 0:
                # differece encoding for the dc pixel
                if (rleconfig.color_component == pixel.Y1) or (
                        rleconfig.color_component == pixel.Y2):

                    accumulator.next = sub(
                        datastream.input_val.signed(), prev_dc_0)

                    prev_dc_0.next = datastream.input_val.signed()

                elif rleconfig.color_component == pixel.Cb:
                    accumulator.next = sub(
                        datastream.input_val.signed(), prev_dc_1)

                    prev_dc_1.next = datastream.input_val.signed()

                elif rleconfig.color_component == pixel.Cr:
                    accumulator.next = sub(
                        datastream.input_val.signed(), prev_dc_2)

                    prev_dc_2.next = datastream.input_val.signed()

                else:
                    pass

                rlesymbols_temp.runlength.next = 0
                rlesymbols_temp.dovalid.next = True

            else:
                # we calculate the runlength here
                if datastream.input_val.signed() == 0:
                    if write_cnt == constants.max_write_cnt:
                        accumulator.next = 0
                        rlesymbols_temp.runlength.next = 0
                        rlesymbols_temp.dovalid.next = True

                    else:
                        zero_cnt.next = zero_cnt + 1

                else:
                    if write_cnt == constants.max_write_cnt:
                        write_cnt.next = 0

                    if zero_cnt <= limit:
                        accumulator.next = datastream.input_val
                        rlesymbols_temp.runlength.next = zero_cnt
                        zero_cnt.next = 0
                        rlesymbols_temp.dovalid.next = True

                    else:
                        accumulator.next = 0
                        rlesymbols_temp.runlength.next = limit
                        zero_cnt.next = zero_cnt - limit
                        rlesymbols_temp.dovalid.next = True
                        zrl_processing.next = True
                        zrl_data_in.next = datastream.input_val
                        divalid.next = False
                        read_cnt.next = read_cnt

        if zrl_processing:
            # if number of zeroes exceeds 15 we stall the input
            if zero_cnt <= limit:
                accumulator.next = zrl_data_in
                rlesymbols_temp.runlength.next = zero_cnt
                zero_cnt.next = 0
                rlesymbols_temp.dovalid.next = True
                divalid.next = divalid_en
                zrl_processing.next = False

            else:
                accumulator.next = 0
                rlesymbols_temp.runlength.next = limit
                zero_cnt.next = zero_cnt - limit
                rlesymbols_temp.dovalid.next = True
                divalid.next = False
                read_cnt.next = read_cnt

        if datastream.start:
            zero_cnt.next = 0
            write_cnt.next = 0


        if rleconfig.sof:
            prev_dc_0.next = 0
            prev_dc_1.next = 0
            prev_dc_2.next = 0

    encoder_inst = entropycoder(
        constants.width_data, clock, reset, accumulator, rlesymbols_temp.size, rlesymbols_temp.amplitude)

    return assign, mainprocessing, encoder_inst
