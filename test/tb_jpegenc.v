
`timescale 1ns/1ps

module tb_jpegenc;
   
   reg clock;   
   reg reset;
   reg jpeg_eof;
   reg jpeg_en;   
   reg [23:0] jpeg_dati;
   
   wire [31:0] jpeg_bits;   
   wire        jpeg_rdy;
   wire [4:0]  jpeg_eof_cnt;
   wire        jpeg_eof_p;   
	       
		
   initial begin
      $dumpfile("vcd/_tb_jpegenc.vcd");
      $dumpvars(0, tb_jpegenc);
   end
      
   initial begin
      $from_myhdl(clock, reset, jpeg_eof, jpeg_en, jpeg_dati);
      $to_myhdl(jpeg_bits, jpeg_rdy, jpeg_eof_cnt, jpeg_eof_p);      
   end

   jpeg_top 
     DUT
       (.clk(clock),
	.rst(reset),
	.end_of_file_signal(jpeg_eof),
	.enable(jpeg_en),
	.data_in(jpeg_dati),
	.JPEG_bitstream(jpeg_bits),
	.data_ready(jpeg_rdy),
	.end_of_file_bitstream_count(jpeg_eof_cnt),
	.eof_data_partial_ready(jpeg_eof_p)
	);   

endmodule
