"""software prototype for backend module"""

import csv


def build_rom_tables(csvfile):
    """build huffman tables"""
    tables_quant = []
    with open(csvfile, 'r') as csvfp:
        csvreader = csv.reader(csvfp, delimiter=',')
        for row in csvreader:
            tables_quant.append(row[0])
    tables_quant = tuple(tables_quant)
    return tables_quant


def build_huffman_rom_tables(csvfile):
    """build huffman tables"""
    code = []
    size = []
    with open(csvfile, 'r') as csvfp:
        csvreader = csv.reader(csvfp, delimiter=',')
        for row in csvreader:
            code.append(row[0])
            size.append(row[1])
    code = tuple(code)
    size = tuple(size)
    return code, size


def divider_ref(dividend, divisor):
    """software implementation of divider"""
    rom_size = 2**8
    rom = [0 for _ in range(rom_size)]
    rom = [0] + [int(round(((2**16)-1)/float(ii)))
                 for ii in range(1, rom_size)]
    rom = tuple(rom)
    divisor_reciprocal = rom[divisor]
    if dividend < 0:
        dividend_d1 = -dividend
    else:
        dividend_d1 = dividend
    mult = (dividend_d1 * divisor_reciprocal)
    mult_s = mult/(2**16)
    if dividend < 0:
        mult_s = -mult_s
    round_ = int((mult/(2**15)) % 2)
    if round_ == 1:
        if dividend >= 0:
            mult_s = mult_s + 1
        else:
            mult_s = int(mult_s - 1)
    return int(mult_s)


def divider(block, color_component):
    """divider reference module"""
    block_out = [0]*64
    tables = build_rom_tables(
        '../jpegenc/subblocks/quantizer/quant_tables.csv')
    tables_len = len(tables)
    rom_tables = [0 for _ in range(tables_len)]
    rom_tables = [int(tables[0])] + [int(
        tables[ii+1]) for ii in range(tables_len-1)]

    rom_tables = tuple(rom_tables)

    if color_component <= 1:
        flag = 0
    else:
        flag = 1

    for i in range(64):
        block_out[i] = divider_ref(block[i], rom_tables[i+flag*64])

    return block_out


def entropy_encode(amplitude):
    """ Model of the entropy encoding

    Arguments:
        amplitude (int): given an integer generate the encoding

    Returns:
        amplitude_ref:
        size_ref:
    """
    if amplitude >= 0:
        amplitude_ref = amplitude
        size_ref = amplitude.bit_length()
    else:
        amplitude_ref = amplitude - 1
        size_ref = abs(amplitude).bit_length()

    return amplitude_ref, size_ref


def runlength(block, color_component, prev_dc_0, prev_dc_1, prev_dc_2):
    """reference for runlength encoder module"""
    output = []
    accumulator = []
    flag = 0
    zero_count = 0

    for i in range(64):
        if i == 0:
            if (color_component == 1) or (color_component == 0):
                accumulator.append(block[i] - prev_dc_0)
                output.append(0)
                prev_dc_0 = block[i]

            elif color_component == 2:
                accumulator.append(block[i] - prev_dc_1)
                output.append(0)
                prev_dc_1 = block[i]

            elif color_component == 3:
                accumulator.append(block[i] - prev_dc_2)
                output.append(0)
                prev_dc_2 = block[i]
            else:
                pass
        else:
            if block[i] == 0:
                zero_count = zero_count + 1
            else:
                if zero_count <= 15:
                    output.append(zero_count)
                    accumulator.append(block[i])
                    zero_count = 0
                else:
                    accumulator.append(0)
                    output.append(15)
                    data = block[i]
                    zero_count = zero_count - 15
                    flag = 1

            while flag == 1:
                if zero_count <= 15:
                    accumulator.append(data)
                    output.append(zero_count)
                    zero_count = 0
                    flag = 0
                else:
                    accumulator.append(0)
                    output.append(15)
                    zero_count = zero_count - 15

            if i == 63:
                if zero_count != 0:
                    accumulator.append(0)
                    output.append(0)

    return (output, accumulator, prev_dc_0, prev_dc_1, prev_dc_2)


def table_huff_gen(filename, base):
    """huffman table generator"""
    code, size = build_huffman_rom_tables(filename)
    rom_code_size = len(code)
    rom_code = [0 for _ in range(rom_code_size)]
    rom_code = [int(code[0], base)] + [int(
        code[ii+1], base) for ii in range(rom_code_size-1)]
    rom_code = tuple(rom_code)
    rom_depth = len(size)
    rom_size = [0 for _ in range(rom_depth)]
    rom_size = [int(size[0])] + [int(size[ii+1]) for ii in range(rom_depth-1)]
    rom_size = tuple(rom_size)
    return rom_size, rom_code


def huffman_ref(
        runlength_block, amplitude_block, size_block,
        color_component, register, pointer):
    """reference model for huffman encoder"""

    size_ac, code_ac = table_huff_gen(
        '../jpegenc/subblocks/huffman/ac_rom.csv', 2)
    size_ac_cr, code_ac_cr = table_huff_gen(
        '../jpegenc/subblocks/huffman/ac_cr_rom.csv', 2)
    size_dc, code_dc = table_huff_gen(
        '../jpegenc/subblocks/huffman/dc_rom.csv', 10)
    size_dc_cr, code_dc_cr = table_huff_gen(
        '../jpegenc/subblocks/huffman/dc_cr_rom.csv', 2)

    for i in range(len(runlength_block)):

        temp1 = format(runlength_block[i], '04b')
        temp2 = format(size_block[i], '04b')
        temp = temp1 + temp2
        temp_int = int(temp, 2)

        if i == 0:
            if color_component < 2:
                vlc_size_ref = size_dc[temp_int]
                vlc_ref = code_dc[temp_int]
            else:
                vlc_size_ref = size_dc_cr[temp_int]
                vlc_ref = code_dc_cr[temp_int]

        else:
            if color_component < 2:
                vlc_size_ref = size_ac[temp_int]
                vlc_ref = code_ac[temp_int]
            else:
                vlc_size_ref = size_ac_cr[temp_int]
                vlc_ref = code_ac_cr[temp_int]

        vlc_size_ref_s = str(0) + str(vlc_size_ref) + 'b'
        vlc_ref_s = format(vlc_ref, vlc_size_ref_s)

        register = register + vlc_ref_s
        pointer = pointer + int(vlc_size_ref)

        size_s = str(0) + str(size_block[i]) + 'b'
        if size_block[i] != 0:
            vli = format(amplitude_block[i], size_s)
            register = register + vli
            pointer = pointer + int(size_block[i])

    return register, pointer


def huffman_final(register, pointer):
    """divide huffman code into bytes"""
    output_huff = []
    num_data_writes = int(pointer/8)
    pointer = pointer - num_data_writes*8
    k = 0
    while num_data_writes > 0:
        output_huff.append(register[k:k+8])
        register = register[k+8:]
        num_data_writes = num_data_writes - 1

    return output_huff, register, pointer


def bytestuffer(block):
    """bytestuffer reference module"""
    for i in range(len(block)):
        if int(block[i], 2) == 255:
            block.insert(i+1, str('0b0'))
    return block


def backend_ref(
        block, prev_dc_0, prev_dc_1, prev_dc_2,
        register, color_component, pointer):
    """backend reference module"""
    accumulator = []
    output = []
    block_rle_in = [0]*64
    block_rle_in = divider(block, color_component)
    output, accumulator, prev_dc_0, prev_dc_1, prev_dc_2 = runlength(
        block_rle_in, 1, prev_dc_0, prev_dc_1, prev_dc_2)
    amplitude = []
    size = []
    for i in range(len(accumulator)):
        amplitude_temp, size_temp = entropy_encode(accumulator[i])
        amplitude.append(amplitude_temp)
        size.append(size_temp)

    output_huff = []
    output_final = []
    register, pointer = huffman_ref(
        output, amplitude, size, color_component, register, pointer)
    output_huff, register, pointer = huffman_final(register, pointer)
    output_final = bytestuffer(output_huff)
    return prev_dc_0, prev_dc_1, prev_dc_2, register, pointer, output_final
