

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
        self.DBus_in.next = data
        self.select.next = True
        self.BE.next = 0xF
        self.RNW.next = False
        ack = False
        while not ack:
            yield self.clock.posedge
            ack = self.XferAck
        self.ABus.next = 0
        self.DBus_in.next = 0
        self.select.next = False
        self.BE.next = 0x0
        yield self.clock.posedge


    def read(self, addr, rval):
        """ read address """
        assert isinstance(rval, SignalType)
        self.ABus.next = addr
        self.select.next = True
        self.BE.next = 0xF
        self.RNW.next = True
        ack = False
        while not ack:
            yield self.clock.posedge
            ack = self.XferAck
        #rval.append(self.DBus_in.val)
        rval.next = self.DBus_in
        self.ABus.next = 0
        self.DBus_out.next = 0
        self.select.next = False
        self.BE.next = 0x0
        self.RNW.next = False
        yield self.clock.posedge


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