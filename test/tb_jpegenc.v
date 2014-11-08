
`timescale 1ns/1ps

module tb_jpegenc;
   
    reg clock;   
    reg reset;

    // version 1 (design1) interface
    reg  [23:0] j1_iram_wdata;
    reg         j1_iram_wren;
    reg         j1_almost_full;
    
    wire        j1_iram_fifo_afull;
    wire [7:0] 	j1_ram_byte;
    wire        j1_ram_wren;
    wire [23:0] j1_ram_wraddr;
    wire [23:0] j1_frame_size;
    
    // version 2 (design2) interface
    reg         j2_eof;
    reg         j2_en;   
    reg  [23:0] j2_dati;
    
    wire [31:0] j2_bits;   
    wire        j2_rdy;
    wire [4:0] 	j2_eof_cnt;
    wire        j2_eof_p;   
	       
		
   initial begin
      $dumpfile("vcd/_tb_jpegenc.vcd");
      $dumpvars(0, tb_jpegenc);
   end
      
   initial begin
      $from_myhdl
	(clock, reset,
	 j1_iram_wdata, j1_iram_wren, j1_almost_full,
	 j2_eof, j2_en, j2_dati
	 );
      $to_myhdl
	(j1_iram_fifo_afull, j1_ram_byte, j1_ram_wren,
	 j1_ram_wraddr, j1_almost_full, j1_frame_size,
	 j2_bits, j2_rdy, 
	 j2_eof_cnt, j2_eof_p
	 );      
   end

   JpegEnc
     DUTV1
       (.CLK(clock),
	.RST(reset),
	/// @todo: OPB bus
	.iram_wdata        (j1_iram_wdata),
	.iram_wren         (j1_iram_wren),
	.iram_fifo_afull   (j1_iram_fifo_afull),
	.ram_byte          (j1_ram_byte),
	.ram_wren          (j1_ram_wren),
	.ram_wraddr        (j1_ram_wraddr),
	.outif_almost_full (j1_almost_full),
	.frame_size        (j1_frame_size)
       );
    
   jpeg_top 
     DUTV2
       (.clk                         (clock),
	.rst                         (reset),
	.end_of_file_signal          (j2_eof),
	.enable                      (j2_en),
	.data_in                     (j2_dati),
	.JPEG_bitstream              (j2_bits),
	.data_ready                  (j2_rdy),
	.end_of_file_bitstream_count (j2_eof_cnt),
	.eof_data_partial_ready      (j2_eof_p)
	);   

endmodule
