#!/bin/sh

pwd
hg clone https://bitbucket.org/jandecaluwe/myhdl
ls myhdl
cd myhdl && hg up -C 0.9-dev 
cd myhdl && setup.py install
cd myhdl/cosimulation/icarus/ && make
cp myhdl/cosimulation/icarus/myhdl.vpi test/
