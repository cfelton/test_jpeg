
**work in progess - don't be suprised if nothing works**

Introduction
============
This repository contains a verification environment to functionally
verify and compare a couple different hardware JPEG encoders.  The 
JPEG encoders used are the cores available at open-cores.

Verification Environment
========================
A stimulus and verification environment was created with Python and
MyHDL.  An image is streamed to the encoder and the output is captured
the hardware JPEG bitstream is compared to a sotware JPEG bistream with
similar settings.

In the future the output of the various encoders will be compared to 
each other.

JPEG Encoders
=============
jpegenc_v1: is the VHDL JPEG encoder converted to Verilog
jpegenc_v2: is the Verilog JPEG encoder.
jpegenc_v3: ...

(@todo: the above need better names)

Getting Started
===============
To run the test the following need to be installed:

  * Icarus Verilog
  
  * Python (currently using 2.7)
  
  * MyHDL
    >> hg clone https://bitbucket.org/jandecaluwe/myhdl
    >> cd myhdl
    >> hg up -C 0.9-dev

  * Python Imaging Library (e.g. pip install Pillow)

The MyHDL VPI module needs to be built and copied to the  test 
directory

  >> cd myhdl/cosimulation/icarus
  >> make 
  >> cp myhdl.vpi <somewhere>/test_jpeg/test
  

Once the tools and installed and the VPI module built the test can
be run.

  >> cd test
  >> python test_jpecenc.py
  
Depending on the test file the test can take significant time to run.
Majority of the time is spent in the Verilog simulator (as seen from
top).  


Results
=======
Someday (probably never) this section might contain some useful information.

Functional
----------
They must work ...

Encoding (compression)
----------------------
awesomely ...

Performance
-----------
and fast ...


