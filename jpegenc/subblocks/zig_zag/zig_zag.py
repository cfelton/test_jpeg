#!/usr/bin/env python
# coding=utf-8

import myhdl
from myhdl import Signal, intbv, always_comb, block

from jpegenc.subblocks.common import outputs_2d, assign_array


class zig_zag_scan(object):

    """Zig-Zag Scan Class

    It is used to produce the zig-zag matrix and as a software
    reference for the zig-zag scan.
    """

    def __init__(self, N):
        """Initialize the zig-zag matrix"""
        self.N = N
        self.zig_zag_matrix = self.build_zig_zag_matrix(N)

    def build_zig_zag_matrix(self, N):
        """Build the zig-zag matrix"""
        """Code taken from http://paddy3118.blogspot.gr/2008/08/zig-zag.html"""
        def zigzag(n):
            indexorder = sorted(((x, y) for x in range(n) for y in range(n)),
                                 key=lambda p: (p[0]+p[1], -p[1] if (p[0]+p[1]) % 2 else p[1]))
            return dict((index, n) for n, index in enumerate(indexorder))

        def zig_zag_list(myarray):
            a = []
            n = int(len(myarray) ** 0.5 + 0.5)
            for x in range(n):
                for y in range(n):
                    a.append(myarray[(x, y)])
            return a

        return zig_zag_list(zigzag(N))

    def zig_zag(self, signal_list):
        """Zig-zag scan function"""
        zig_zag_result = [None for i in range(self.N**2)]
        for i in range(self.N**2):
            a = self.zig_zag_matrix[i]
            zig_zag_result[a] = signal_list[i]

        return zig_zag_result


@block
def zig_zag(inputs, outputs, N=8):
    """Zig-Zag Module

    This module performs the zig-zag reorderding. According to the
    zig-zag matrix the input list of signals is reordered.

    Inputs:
        List of signals of a NxN block
    Outputs:
        Reordered list of signals of a NxN block
    Parameters:
        N = the size of the NxN block
    """
    zig_zag_obj = zig_zag_scan(N)
    zig_zag_rom = tuple(zig_zag_obj.zig_zag_matrix)
    index = Signal(intbv(0, min=0, max=N**2))
    output_sigs = [Signal(intbv(0, min =-inputs.out_range, max=inputs.out_range))
                   for _ in range(N**2)]
    input_sigs = [Signal(intbv(0, min =-inputs.out_range, max=inputs.out_range))
                   for _ in range(N**2)]

    @always_comb
    def zig_zag_assign():
        if inputs.data_valid:
            for i in range(N**2):
                index = zig_zag_rom[i]
                output_sigs[int(index)].next = input_sigs[int(i)]
            outputs.data_valid.next = inputs.data_valid

    output_assignments =assign_array(outputs.out_sigs, output_sigs)
    input_assignments = assign_array(input_sigs, inputs.out_sigs)

    return zig_zag_assign, output_assignments, input_assignments







