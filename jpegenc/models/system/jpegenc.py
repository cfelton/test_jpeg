
def jpegenc(clock, reset, video):
    block_size = (8, 8)

    pixels = PixelStream()  # RGBStream()
    block_buffer(video, pixels, block_size=block_size)

    ycbcr = YCbCrStream()
    color_conversion(pixels, ycbcr)

    frequencies = ImageBlock()
    mdct(ycbcr, frequencies)

    quantized = PixelStream()
    quantization(frequencies, quantized)

    symbols = DataStream()
    run_length_encoder(quantized, symbols)

    packed = DataStream()
    huffman_encoder(symbols, packed)

    jpeg = DataStream()
    jfif_formatter(packed, jpeg)

    return myhdl.instances()
