
[![Build Status](https://travis-ci.org/cfelton/test_jpeg.svg?branch=master)](https://travis-ci.org/cfelton/test_jpeg)
[![Code Health](https://landscape.io/github/cfelton/test_jpeg/master/landscape.svg?style=flat-square)](https://landscape.io/github/cfelton/test_jpeg/master)
[![Documentation Status](https://readthedocs.org/projects/jpegenc/badge/?version=latest)](http://jpegenc.readthedocs.io/en/latest/?badge=latest)

 

Introduction
============
This repository is a development sandbox.  The respository 
contains three related development efforts:

1. VHDL to Verilog conversion of the first JPEG-encoder reference 
   (rational explained below).
2. MyHDL verification and co-simulation environment, tests will 
   functionally verify and compare the reference JPEG-encoders.
3. A MyHDL implementation of a JPEG-encoder.

The JPEG encoders used are the cores available at open-cores in 
addition to JPEG encoders being developed.  This is a WIP and not 
fully complete.


Verification Environment
========================
A stimulus and verification environment was created with Python and
MyHDL.  An image is streamed to the encoder and the output is captured.
The hardware generated JPEG bitstream is compared to a software JPEG 
bitstream with similar settings.

In the future the output of the various encoders will be compared to 
each other as well as the encoder performance (.e.g. max fps).


JPEG Encoders
=============

   - hdl/jpegenc_v1: [VHDL JPEG encoder](http://opencores.org/project,mkjpeg) converted to Verilog
   - hdl/jpegenc_v2: [OC Verilog JPEG](http://opencores.org/project,jpegencode) encoder.
   - jpegenc: A fresh (non-ported) MyHDL implementation, `jpegenc` is a Python package
     being developed.

<!-- (@todo: the above need better names?) -->


Getting Started
===============
To run the test the following needs to be installed:

  * Icarus Verilog
  * Python (currently using 2.7)
  * MyHDL
  * Python Imaging Library (e.g. pip install Pillow)


The MyHDL VPI module needs to be built and copied to the test 
directory.

```
>> cd myhdl/cosimulation/icarus
>> make 
>> cp myhdl.vpi <somewhere>/test_jpeg/test
```  

Once the tools and installed and the VPI module built the test can
be run.

```
>> cd test
>> python test_jpecenc.py
```

Depending on the test file the test can take significant time to run.
Majority of the time is spent in the Verilog simulator (as seen from
*top*).  

<!-- 
MyHDL has some inefficiencies with Icarus
([Icarus Cosimulation](http://docs.myhdl.org/en/latest/manual/cosimulation.html#icarus-verilog)).
-->

<!--
    limited capture no tracing
    10:  
    20:
    100: 

    limited capture Verilog tracing
           Total   V1    V2
    100:   5.8     3.24  5.19
    200:   6.7     3.53  6.15
    400:   9.5     4.00  8.89
    800:                 14.03
    1000:
-->

```
    PID   COMMAND      %CPU TIME     MEM    
    3061  vvp          82.7 09:45.51 8200K  
    3048  Python       18.7 02:16.07 14M   
```

Cosimulation time for a 80x80 pixel image and not VCD tracing.
 
``` 
    CPython execution time:
    pypy execution time:
```

Cosimulation time for a 80x80 pixel image and VCD tracing.

```
    CPython execution time:
    pypy execution time:
```

As mentioned, majority of the time is spent in the Verilog 
simulator the Python run-time has little effect.


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
and fast ... correct?


Progress Log
==============
 
   **28-Dec-2014** : Conversion error was found in V1, V1 finishes
     compressing the frame.  V2 has error with small images, this 
     might be a design limitation.

   **07-Dec-2014** : Neither encoder completes successfully with a 
     small test image, currently debugging (design1 (v1) conversion 
     complete need to find any errors in conversion).  The test 
     environment will stream the image in and complete shortly after 
     the image has been streamed in.

   **05-Dec-2014** : Design1 conversion to verilog is mostly complete, 
     spending some time verifying.

   **09-Nov-2014** : The test environment will stream an image to both
     the design1 and design2 encoders.  The output is not interrogated
     (yet).  Design1 conversion to verilog is incomplete.


Things to be completed
----------------------

   1. [ ] Use Python3 as the default python verson.
   
   1. [ ] Check encoded bitstreams, determine metrics to compare 
          encoders.

   1. [X] Debug the small test image, neither encoder appears to
          finish.

   1. [X] Finish converting desing1 to Verilog.
    
   
Last MyHDL master version tested
--------------------------------
   - `80b1864`: 16-Jul-2015
   - `7c7bb58`: 27-Apr-2015



