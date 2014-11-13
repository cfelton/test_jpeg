

from myhdl import *

class OPBBus(object):
    def __init__(self, clock, reset):
        self.clock = clock
        self.reest = reset
        self.ABus = Signal(intbv(0)[32:])
        self.BE = Signal(intbv(0)[4:])
        self.DBus_in = Signal(intbv(0)[32:])
        self.RNW = Signal(bool(0))
        self.select = Signal(bool(0))
        self.DBus_out = Signal(intbv(0)[32:])
        self.XferAck = Signal(bool(0))
        self.retry = Signal(bool(0))
        self.toutSup = Signal(bool(0))
        self.errAck = Signal(bool(0))

    def write(self, addr, data):
        """ write to address """
        self.ABus.next = addr
        self.DBus_out.next = data
        self.select.next = True
        self.BE.next = 0xF
        while not self.XferAck:
            yield self.clock.posedge
        self.ABus.next = 0
        self.DBus.next = 0
        self.select.next = False
        self.BE.next = 0x0


    def read(self, addr):
        """ read address """
        pass

    def interconnect(self, *per):
        """ """
        num_per = len(per)
        @always_comb
        def rtl():
            self.DBus_in.next = 0
            self.XferAck.next = False
            for ii in range(num_per):
                self.DBus_in.next = self.DBus_in | per[ii].DBus_in
                self.XferAck.next = self.XferAck | per[ii].XferAck

        return rtl