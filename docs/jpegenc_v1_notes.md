General Notes
=============
V1 JPEG encoder standard flow

### BUF_FIFO (Input FIFO) 
Pixels are streamed into this FIFO, this FIFO will ...  
This FIFO will write the input-stream into RAM

### FDCT (2D DCT) 
This is the next module in the processing chain, note the 
`CtrlSM` is coordinating (some?).
          
FIFO Read Process (IRAM read process) this works independently
(almost) of the main controller.  This should transfer from 
`BUF_FIFO` (Input FIFO) and move to the `FRAM1` (IRAM)?

Read process job:
   * at SOF start reading BUF_FIFO if not empty
   * process (move) data at a higher rate
   * move data from BUF_FIFO to intermediate RAM (FRAM) and this
     is used by MDCT
     * stalls reading when FIFO1 has less that 64 words space
     * stalls with BUF_FIFO empty	

Key signals(?): (~line 243 process, convert to state-machine?)
    `x_pixel_cnt`:
    `y_line_cnt`:
    `input_rd_cnt`:
    `cmp_idx`:
    `start_int`: 
    `bf_fifo_rd`:
    `fram1_rd`:
    `fram1_raddr`:
    `fram1_line_cnt`:
    `fram1_pix_cnt`:

Input FIFO (BUF_FIFO) --> FRAM --> (RBG2YCbCr) MDCT 


### CtrlSM (system state-machine) 
this module controls and coordinates
the encoder.  This is the pipeline controller, coordinates all 
the different processing blocks.

Main states (stages?):

    IDLES   1 : Waiting for a pixel-stream
    JFIF    2 : Generation of JFIF header
    HORIZ   3 : Encoding process blocks of 16x8 samples until
                horizontal counter reaches width of image
    COMP    4 : Component processing, process one 16x8 (8x8?)
                block for each component in interleaved fashion
                including subsampling
    VERT    5 : Reset horizontal counter and advance vertical
    EOI     6 : End of image

The documentation indicates most of the processing time will be
consumed processing the 16x8 blocks, toggling between the HORIZ
and VERT states finish with COMP in between and a final transition
of VERT to EOI, these are mainly driven by `x_cnt` and `y_cnt` in 
the code this is the `RSM_x_cnt` and `RSM_y_cnt`.  The state-machine
will remain in HORIZ while `RSM_x_cnt` < `img_size_x`.


The documentation outlines the pipeline processing as
(processing blocks):

    1. FDCT
    2. ZIGZAG
    3. Quantizer
    4. RLE (run-length encoder)
    5. Huffman
    6. Byte stuffer

The controller (appears) to control the different processing blocks 
and keeps track of which stages are work, there are 6 stages.

  idle  - stages in idle
  start - stages started 



