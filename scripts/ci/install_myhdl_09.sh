#!/bin/sh

pwd
mkdir tmp
git clone https://github.com/jandecaluwe/myhdl tmp/myhdl
ls .
ls tmp/myhdl
cd tmp/myhdl
python setup.py install
cd cosimulation/icarus/ 
make
# copy the VPI to the test directory
cp myhdl.vpi ../../../../test/
