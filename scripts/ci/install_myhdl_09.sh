#!/bin/sh

pwd
hg clone https://bitbucket.org/jandecaluwe/myhdl
ls .
ls myhdl
cd myhdl && hg up -C 0.9-dev 
cd myhdl && python setup.py install
cd myhdl/cosimulation/icarus/ && make
cp myhdl/cosimulation/icarus/myhdl.vpi test/
