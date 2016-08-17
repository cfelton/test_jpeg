"""This module tests the functionality and conversion of Entropy Coder"""

from myhdl import block, instance, modbv
from myhdl import intbv, ResetSignal, Signal, StopSimulation
from myhdl.conversion import verify

from jpegenc.subblocks.backend.backend import backend
from jpegenc.subblocks.backend.backend_soft import backend_ref

from jpegenc.testing import run_testbench
from jpegenc.testing import (clock_driver, reset_on_start,
                             pulse_reset, toggle_signal)


block_1 = [0]*64
for i in range(64):
    block_1[i] = i % 25

block_2 = [0]*64
for i in range(64):
    block_2[i] = i % 16

block_3 = [0]*64
for i in range(64):
    block_3[i] = i % 47

block_4 = [0]*64
for i in range(64):
    block_4[i] = i % 28

block_5 = [0]*64
for i in range(64):
    block_5[i] = i % 40

block_6 = [0]*64
for i in range(64):
    block_6[i] = i % 31


def backend_soft():
    """backend reference model"""
    # 1st block
    prev_dc_0 = 0
    prev_dc_1 = 0
    prev_dc_2 = 0
    pointer = 0
    register = []
    register = str(register)
    register = register[2:]
    outputs_fin = []

    # 1st rgb block
    prev_dc_0, prev_dc_1, prev_dc_2, register, pointer, outputs = backend_ref(
        block_1, prev_dc_0, prev_dc_1, prev_dc_2, register, 1, pointer)

    for ind in range(len(outputs)):
        outputs_fin.append(outputs[ind])

    prev_dc_0, prev_dc_1, prev_dc_2, register, pointer, outputs = backend_ref(
        block_2, prev_dc_0, prev_dc_1, prev_dc_2, register, 2, pointer)

    for i in range(len(outputs)):
        outputs_fin.append(outputs[i])

    prev_dc_0, prev_dc_1, prev_dc_2, register, pointer, outputs = backend_ref(
        block_3, prev_dc_0, prev_dc_1, prev_dc_2, register, 2, pointer)

    for i in range(len(outputs)):
        outputs_fin.append(outputs[i])

    # need to fix color component
    # 2nd rgb block
    prev_dc_0, prev_dc_1, prev_dc_2, register, pointer, outputs = backend_ref(
        block_4, prev_dc_0, prev_dc_1, prev_dc_2, register, 3, pointer)

    for i in range(len(outputs)):
        outputs_fin.append(outputs[i])

    prev_dc_0, prev_dc_1, prev_dc_2, register, pointer, outputs = backend_ref(
        block_5, prev_dc_0, prev_dc_1, prev_dc_2, register, 4, pointer)

    for i in range(len(outputs)):
        outputs_fin.append(outputs[i])

    prev_dc_0, prev_dc_1, prev_dc_2, register, pointer, outputs = backend_ref(
        block_6, prev_dc_0, prev_dc_1, prev_dc_2, register, 5, pointer)

    for i in range(len(outputs)):
        outputs_fin.append(outputs[i])

    return outputs_fin


def test_backend():
    """
    We will test the functionality of entropy coder in this block

    constants:

    width_data : width of the input data
    size_data : size required to store the data
    width_addr : width of the address

    """

    # width of the input data
    width_data = 12
    write_addr = 7

    # clock and reset signals
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # declaration of input signal
    data_in = Signal(intbv(0)[width_data:])
    write_addr = Signal(modbv(0)[7:])
    ready = Signal(bool(0))
    data_out = Signal(intbv(0)[width_data:])
    valid_data = Signal(bool(0))
    start_block = Signal(bool(0))
    addr = Signal(intbv(0)[24:])
    num_enc_bytes = Signal(intbv(0)[24:])

    @block
    def bench_backend():
        """This bench is used to test the functionality"""

        # instantiate module and clock
        inst = backend(clock, reset, start_block, data_in,
                       write_addr, valid_data, data_out,
                       ready, addr, num_enc_bytes)

        inst_clock = clock_driver(clock)

        @instance
        def tbstim():
            """stimulus generates inputs for entropy coder"""

            # reset the module
            output_model = [0]*64
            yield pulse_reset(reset, clock)

            # write Y data into input buffer
            valid_data.next = True
            yield clock.posedge
            write_addr.next = 64
            for i in range(64):
                data_in.next = i % 25
                yield clock.posedge
                write_addr.next = write_addr + 1
            valid_data.next = False
            yield clock.posedge

            for _ in range(35):
                yield clock.posedge

            # start the blocks
            yield toggle_signal(start_block, clock)

            # write Cb data into input buffer
            valid_data.next = True
            yield clock.posedge
            for i in range(64):
                data_in.next = i % 16
                yield clock.posedge
                write_addr.next = write_addr + 1
            valid_data.next = False
            yield clock.posedge
            while not ready:
                yield clock.posedge

            yield toggle_signal(start_block, clock)
            # write  Cr data into input buffer
            valid_data.next = True
            yield clock.posedge
            for i in range(64):
                data_in.next = i % 47
                yield clock.posedge
                write_addr.next = write_addr + 1
            valid_data.next = False
            yield clock.posedge
            while not ready:
                yield clock.posedge

            yield toggle_signal(start_block, clock)
            # write Y data into input buffer
            valid_data.next = True
            yield clock.posedge
            for i in range(64):
                data_in.next = i % 28
                yield clock.posedge
                write_addr.next = write_addr + 1
            valid_data.next = False
            yield clock.posedge
            while not ready:
                yield clock.posedge

            yield toggle_signal(start_block, clock)
            # write Cb data into input buffer
            valid_data.next = True
            yield clock.posedge
            for i in range(64):
                data_in.next = i % 40
                index = int(addr)
                output_model[index] = int(data_out)
                yield clock.posedge
                write_addr.next = write_addr + 1
            valid_data.next = False
            yield clock.posedge

            yield toggle_signal(start_block, clock)
            # write Cr data into input buffer
            valid_data.next = True
            yield clock.posedge
            for i in range(64):
                data_in.next = i % 31
                index = int(addr)
                output_model[index] = int(data_out)
                yield clock.posedge
                write_addr.next = write_addr + 1
            valid_data.next = False
            yield clock.posedge
            while not ready:
                yield clock.posedge

            yield toggle_signal(start_block, clock)
            while not ready:
                index = int(addr)
                output_model[index] = int(data_out)
                yield clock.posedge

            yield toggle_signal(start_block, clock)
            while not ready:
                index = int(addr)
                output_model[index] = int(data_out)
                yield clock.posedge

            yield toggle_signal(start_block, clock)
            while not ready:
                index = int(addr)
                output_model[index] = int(data_out)
                yield clock.posedge

            yield toggle_signal(start_block, clock)
            while not ready:
                index = int(addr)
                output_model[index] = int(data_out)
                yield clock.posedge

            print ("===================")

            for i in range(addr):
                print ("outputs_hdl %d" % output_model[i])
            print ("======================")
            # get outputs from reference values
            output_ref = []
            output_ref = backend_soft()
            for i in range(len(output_ref)):
                print ("outputs_soft %d" % int(output_ref[i], 2))
            print ("===========================")
            # compare reference and HDL outputs
            for i in range(len(output_ref)):
                assert int(output_ref[i], 2) == output_model[i]

            raise StopSimulation

        return tbstim, inst, inst_clock

    run_testbench(bench_backend)


def test_backend_conversion():
    """
    We will test the functionality of entropy coder in this block

    constants:

    width_data : width of the input data
    size_data : size required to store the data
    width_addr : width of the address

    """

    # width of the input data
    width_data = 12
    write_addr = 7

    # clock and reset signals
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=True, async=True)

    # declaration of input signal
    data_in = Signal(intbv(0)[width_data:])
    write_addr = Signal(modbv(0)[7:])
    ready = Signal(bool(0))
    data_out = Signal(intbv(0)[width_data:])
    valid_data = Signal(bool(0))
    start_block = Signal(bool(0))
    addr = Signal(intbv(0)[24:])
    num_enc_bytes = Signal(intbv(0)[24:])

    @block
    def bench_backend_conversion():
        """This bench is used to test the functionality"""

        # instantiate module and clock
        inst = backend(clock, reset, start_block, data_in,
                       write_addr, valid_data, data_out,
                       ready, addr, num_enc_bytes)

        inst_clock = clock_driver(clock)
        inst_reset = reset_on_start(reset, clock)

        @instance
        def tbstim():
            """testbench for conversion purpose"""
            yield clock.posedge
            print("Conversion done!!")
            raise StopSimulation

        return tbstim, inst, inst_clock, inst_reset

    verify.simulator = 'iverilog'
    assert bench_backend_conversion().verify_convert() == 0


if __name__ == "__main__":
    test_backend()
    test_backend_conversion()
