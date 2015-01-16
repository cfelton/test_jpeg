#!/bin/sh

pwd
mkdir tmp
hg clone https://bitbucket.org/jandecaluwe/myhdl tmp/myhdl
ls .
ls tmp/myhdl
cd tmp/myhdl
hg up -C 0.9-dev 
python setup.py install
cd cosimulation/icarus/ 
make
# copy the VPI to the test directory
cp myhdl.vpi ../../../../test/
