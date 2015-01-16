#!/bin/sh

hg clone https://bitbucket.org/jandecaluwe/mhydl tmp/myhdl
cd tmp/myhdl && hg up -C 0.9-dev 
cd tmp/myhdl && setup.py install
cd tmp/myhdl/cosimulation/icarus/ && make
cp tmp/myhdl/cosimulation/icarus/myhdl.vpi test/
