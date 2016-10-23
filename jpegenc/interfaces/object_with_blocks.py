
import myhdl


g_inst_id = 0
g_names = set()


class ObjectWithBlocks(object):
    def __init__(self, name="object"):
        """

        Args:
            name: a name for the object, this will be used for
             the instance names in the tracing and conversion.
        """
        global g_inst_id, g_names

        self.inst_id = g_inst_id
        g_inst_id += 1
        self.use_id = True
        self._name = name
        assert self.name not in g_names, '@E: name exists'
        g_names.add(self.name)

    @property
    def name(self):
        nm = self._name
        if self.use_id:
            nm = "{}_{}".format(nm, self.inst_id)
        return nm

    @name.setter
    def name(self, nm):
        global g_names
        assert nm not in g_names, "@E: setting name, already exists"
        g_names.remove(self.name)
        self._name = nm
        self.use_id = False

    @myhdl.block
    def __call__(self, *ports, **params):
        inst = self.process(*ports, **params)
        inst.name = self.name
        return inst

    @myhdl.block
    def owb(self, *ports, **params):
        """Get the process for this object.

        The naming for the myhld blocks has changed considerably in
        1.0dev.  For most uses it is not

        Args:
            *ports: ports for the process
            **params: parameters for the process

        Returns: myhdl Block object

        """
        inst = self.process(*ports, **params)
        inst.name = self.name
        return inst

    def process(self, *ports, **params):
        raise NotImplementedError
