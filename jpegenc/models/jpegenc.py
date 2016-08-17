
import myhdl
from rhea import Global, Clock, Reset

from .interfaces import DataStream, PixelStream, RGBStream
from .subblocks import VideoStreamSource


def jpegenc(clock, reset, video, jpeg_bitstream):
    block_size = (8, 8)
    num_blk_cols, num_blk_rows = block_size

    clock = Clock(0, frequency=100e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Generate a video stream, input to the JPEG encoder
    video = VideoStreamSource()
    video_inst = video.process(glbl)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # JPEG encoder subblocks, the main components of a JPEG encoder.

    # ~~~[Row Buffer]~~~
    # The first stage is simply to buffer enough rows to create a
    # block.  The JPEG encoder works on blocks.
    # @todo: the output of the row_buffer should maybe be an ImageBlock,
    #        this will provide more flexibility.

    pixels = RGBStream()
    row_buffer_inst = video.row_buffer(video, pixels)

    # block_buffer(video, pixels, block_size=block_size)

    # ~~~[Color Conversion]~~~
    #
    ycbcr = YCbCrStream()
    color_conversion(pixels, ycbcr)

    # ~~~[Discrete Cosine Transform]~~~
    #
    frequencies = ImageBlock()
    mdct(ycbcr, frequencies)

    # ~~~[Quantization]~~~
    quantized = PixelStream()
    quantization(frequencies, quantized)

    # ~~~[Run Length Encoding]~~~
    symbols = DataStream()
    run_length_encoder(quantized, symbols)

    # ~~~[Huffman Encoding]~~~
    packed = DataStream()
    huffman_encoder(symbols, packed)

    # ~~~[Byte Stuffer]~~~
    jpeg = DataStream()
    jfif_formatter(packed, jpeg)

    return myhdl.instances()
