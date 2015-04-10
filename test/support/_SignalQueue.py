#
# Copyright (c) 2013 Christopher Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import Queue
from myhdl import Signal, delay

class SignalQueue(Queue.Queue):
    def __init__(self, maxsize=0):
        self.Empty = Signal(True)
        self.Full = Signal(False)
        self.maxsize = maxsize
        self._max = 0
        Queue.Queue.__init__(self, maxsize=maxsize)

    def put(self, item, block=True, timeout=None):
        assert timeout is None, "Timeout not yet implemented"
        #print("block %s full %s" % (block, self.Full))
        if block and self.Full:
            yield self.Full.negedge
        Queue.Queue.put(self, item, block=False, timeout=None)
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
        #print("block %s empty %s %d" % (block, self.Empty, self.qsize()))
        if block and self.Empty:
            yield self.Empty.negedge
        item[0] = Queue.Queue.get(self, block=False, timeout=None)
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
