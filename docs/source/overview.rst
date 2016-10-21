
Overview
========
The `jpegenc` package is a JPEG encoder implemented in
MyHDL_.  The JPEG encoder is intended to be
flexible with reusable subblocks.  This project also includes a
verification environment for the encoder.

.. _MyHDL: http://www.myhdl.org

The following figure outlines the main subblocks in the system.

.. figure:: https://cloud.githubusercontent.com/assets/766391/18724671/e3eff6e8-8002-11e6-9dfe-9a03379a06fb.png
    :scale: 80%

    The JPEG encoder system diagram

The subblocks were designed to be independent and process an
image stream.


Uses
----
   * (M)JPEG real-time video compression.
   * Framework for investigation image and video compression.


Goals
-----

   * Easy to use and understand JPEG encoder implementation.
   * Flexible (modular) and reusable subblocks.
   * Base set of blocks to build various image and video encoders.


Measurements
------------

.. toctree::
    :maxdepth: 1

     Coverage<./subblocks/coverage.rst>
     Implementation Results<./subblocks/impl.rst>

