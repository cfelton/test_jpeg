
import myhdl


g_inst_id = 0


class ObjectWithBlocks(object):
    def __init__(self, name="owb"):
        global g_inst_id
        self.inst_id = g_inst_id
        g_inst_id += 1
        self._name = name

    @property
    def name(self):
        nm = self._name
        if hasattr(self, __name__):
            nm = self.__name__
        nm = "{}_{}".format(nm, self.inst_id)
        return nm

    @myhdl.block
    def __call__(self, *ports, **params):
        inst = self.process(*ports, **params)
        inst.name = self.name
        return inst

    def process(self, *ports, **params):
        raise NotImplementedError
