
try:
    from Queue import Queue
except:
    from queue import Queue

from myhdl import Signal, delay


class SignalQueue(Queue):
    def __init__(self, maxsize=0):
        self.Empty = Signal(True)
        self.Full = Signal(False)
        self.maxsize = maxsize
        self._max = 0
        Queue.__init__(self, maxsize=maxsize)

    def put(self, item, block=True, timeout=None):
        assert timeout is None, "Timeout not yet implemented"
        # print("block %s full %s" % (block, self.Full))
        if block and self.Full:
            yield self.Full.negedge
        Queue.put(self, item, block=False, timeout=None)
        self._max = max(self._max,self.qsize())
        self.Empty.next = False
        if self.qsize() == self.maxsize and self.maxsize > 0:
            self.Full.next = True
        if self.Empty or not self.Full:
            yield delay(1)

    def put_nowait(self, item):
        self.put(item, Block=False, timeout=None)

    def get(self, item, block=True, timeout=None):
        assert timeout is None, "Timeout not yet implemented"
        # print("block %s empty %s %d" % (block, self.Empty, self.qsize()))
        if block and self.Empty:
            yield self.Empty.negedge
        item[0] = Queue.get(self, block=False, timeout=None)
        if self.qsize() == 0:
            self.Empty.next = True
        self.Full.next = False
        if not self.Empty or self.Full:
            yield delay(1)        
    
    def get_nowait(self, item):
        yield self.get(item, block=False, timeout=None)

    def __str__(self):
        s = 'len %d, max %d'%(self.qsize(),self._max)
        return s

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.qsize()
