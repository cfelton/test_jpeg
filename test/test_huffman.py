"""The functionality of entire
    Huffman Module is checked here"""

from myhdl import StopSimulation
from myhdl import block
from myhdl import ResetSignal, Signal, instance
from myhdl.conversion import verify

from jpegenc.subblocks.huffman import HuffmanCntrl, ImgSize, huffman
from jpegenc.subblocks.huffman import HuffmanDataStream, HuffBufferDataBus

from jpegenc.testing import (clock_driver, reset_on_start,
                             pulse_reset, toggle_signal,)

from jpegenc.testing import run_testbench
from jpegenc.subblocks.rle import Component


from huff_test_inputs import (vli_test_y, vli_size_test_y, runlength_test_y,
                              vli_test_cb, vli_size_test_cb,
                              runlength_test_cb, vli_test_cr,
                              vli_size_test_cr, runlength_test_cr,)


def write_block(
        input_stream, control_unit, input_fifo_empty, color,
        input_pixel_vli, input_runlength_test, input_vli_size_test, clock):
    """write data into the huffman module"""

    assert isinstance(input_stream, HuffmanDataStream)
    assert isinstance(control_unit, HuffmanCntrl)

    # select color component
    control_unit.color_component.next = color
    # start pulse generated
    control_unit.start.next = True
    yield clock.posedge
    control_unit.start.next = False
    # stream input data into the block

    # process first data input
    input_stream.vli.next = input_pixel_vli[0]
    input_stream.runlength.next = input_runlength_test[0]
    input_stream.vli_size.next = input_vli_size_test[0]
    yield clock.posedge
    input_stream.data_valid.next = True
    yield clock.posedge
    input_stream.data_valid.next = False
    yield clock.posedge

    # process more 63 inputs
    for i in range(63):
        # input runlength, variable length integer codes
        input_stream.runlength.next = input_runlength_test[i+1]
        input_stream.vli_size.next = input_vli_size_test[i+1]
        input_stream.vli.next = input_pixel_vli[i+1]
        yield clock.posedge
        # extra clock after first input
        if i == 0:
            yield clock.posedge
        yield clock.posedge
        # validate input data
        input_stream.data_valid.next = True
        yield clock.posedge
        input_stream.data_valid.next = False
        # input fifo empty signal asserted
        if i == 62:
            input_fifo_empty.next = True
        yield clock.posedge
    # wait for some clocks for computation to be done
    for _ in range(7):
        yield clock.posedge
    input_fifo_empty.next = False


def read_block(output_data_bus, clock):
    """This function reads the data from FIFO"""

    assert isinstance(output_data_bus, HuffBufferDataBus)
    # enable read signal
    yield toggle_signal(output_data_bus.read_req, clock)
    print ("%s" % bin(output_data_bus.huf_packed_byte))
    # read all the data from FIFO
    while not output_data_bus.fifo_empty:
        yield toggle_signal(output_data_bus.read_req, clock)
        print ("%s" % bin(output_data_bus.huf_packed_byte))


def test_huffman():
    """This test checks the functionality of the Run Length Encoder"""

    # clock and reset signals
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    # width of the runlength
    width_runlength = 4
    # width of the vli size
    width_size = 4
    # width of the vli amplitude ref
    width_amplitude = 12
    # width of address register
    width_addr = 6
    # width of the output data
    width_packed_byte = 8
    # image width
    width = 8
    # image height
    height = 8

    huffmandatastream = HuffmanDataStream(
        width_runlength, width_size, width_amplitude, width_addr)
    assert isinstance(huffmandatastream, HuffmanDataStream)

    bufferdatabus = HuffBufferDataBus(width_packed_byte)
    assert isinstance(bufferdatabus, HuffBufferDataBus)

    huffmancntrl = HuffmanCntrl()
    assert isinstance(huffmancntrl, HuffmanCntrl)

    # color component class
    component = Component()
    assert isinstance(component, Component)

    # image size class
    img_size = ImgSize(width, height)
    assert isinstance(img_size, ImgSize)

    # input fifo is empty
    rle_fifo_empty = Signal(bool(0))

    @block
    def bench_huffman():
        """bench to test the functionality of RLE"""

        inst = huffman(clock, reset, huffmancntrl, bufferdatabus,
                       huffmandatastream, img_size, rle_fifo_empty)
        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """Huffman input tests given here"""

            # reset the stimulus before sending data in
            yield pulse_reset(reset, clock)

            bufferdatabus.buffer_sel.next = False
            # send y1 component into the module
            color = component.y1_space
            yield write_block(huffmandatastream, huffmancntrl, rle_fifo_empty,
                              color, vli_test_y, runlength_test_y,
                              vli_size_test_y, clock)
            print ("=======================================")

            # read y1 component from the double FIFO
            bufferdatabus.buffer_sel.next = True
            yield read_block(bufferdatabus, clock)
            print ("==============================")

            # send cb component into the module
            color = component.cb_space
            yield write_block(huffmandatastream, huffmancntrl, rle_fifo_empty,
                              color, vli_test_cb, runlength_test_cb,
                              vli_size_test_cb, clock)
            print ("==========================================")

            # read cb component from the double FIFO
            bufferdatabus.buffer_sel.next = False
            yield clock.posedge
            yield read_block(bufferdatabus, clock)
            print ("==============================")

            # send cr component into the module
            color = component.cr_space
            yield write_block(huffmandatastream, huffmancntrl, rle_fifo_empty,
                              color, vli_test_cr, runlength_test_cr,
                              vli_size_test_cr, clock)
            print ("============================")

            # read cr component from the double FIFO
            bufferdatabus.buffer_sel.next = True
            yield clock.posedge
            yield read_block(bufferdatabus, clock)
            print ("==============================")

            yield toggle_signal(huffmancntrl.sof, clock)

            raise StopSimulation

        return tbstim, inst_clock, inst

    run_testbench(bench_huffman)


def test_block_conversion():
    """Test bench used for conversion purpose"""

    # clock and reset signals
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=True)

    # width of the runlength
    width_runlength = 4
    # width of the vli size
    width_size = 4
    # width of the vli amplitude ref
    width_amplitude = 12
    # width of address register
    width_addr = 6
    # width of the output data
    width_packed_byte = 8
    # image width
    width = 8
    # image height
    height = 8

    huffmandatastream = HuffmanDataStream(
        width_runlength, width_size, width_amplitude, width_addr)
    assert isinstance(huffmandatastream, HuffmanDataStream)

    bufferdatabus = HuffBufferDataBus(width_packed_byte)
    assert isinstance(bufferdatabus, HuffBufferDataBus)

    huffmancntrl = HuffmanCntrl()
    assert isinstance(huffmancntrl, HuffmanCntrl)

    # color component class
    component = Component()
    assert isinstance(component, Component)

    # image size class
    img_size = ImgSize(width, height)
    assert isinstance(img_size, ImgSize)

    # input fifo is empty
    rle_fifo_empty = Signal(bool(0))

    @block
    def bench_entropycoder():
        """This bench is used for conversion purpose"""

        # instantiate module, clock and reset
        inst = huffman(clock, reset, huffmancntrl, bufferdatabus,
                       huffmandatastream, img_size, rle_fifo_empty)
        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            """dummy tests for conversion purpose"""

            yield clock.posedge
            print ("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    # verify conversion using iverilog
    verify.simulator = 'iverilog'
    assert bench_entropycoder().verify_convert() == 0


if __name__ == "__main__":
    test_huffman()
    test_block_conversion()
