
This directory contains the MyHDL implementation of a JPEG
encoder.  The implementation here is independent of the 
Verilog and VHDL reference designs used in this project.
The [hdl](https://github.com/cfelton/test_jpeg/tree/master/hdl) 
directory.  In the [hdl](https://github.com/cfelton/test_jpeg/tree/master/hdl) 
directory is MyHDL code that is direct ports of the V* 
reference implementations.  The impementations in this directory
an not intended to be straight ports but new implmentations 
that are modular, scalable, and leverage the MyHDL design 
patterns.

The envisioned Python package structure:

```
    jpegenc
       docs
       jpegenc
           models
           hdl
        setup.py
        test
```  

This directory is being used as a development sandbox because
the tests for the V* verification can be utilized and extended.
At some point in the future if the MyHDL implementation is 
complete it should have it own repository for the python only
package.
