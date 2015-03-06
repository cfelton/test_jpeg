#!/bin/sh

git clone https://github.com/jandecaluwe/myhdl
python myhdl/setup.py install
make -C myhdl/cosimulation/icarus
# copy the VPI to the test directory
cp myhdl.vpi ../../test/
