// File ../design/ZIGZAG_c.VHD translated with vhd2vl v2.4 VHDL to Verilog RTL translator
// vhd2vl settings:
//  * Verilog Module Declaration Style: 1995

// vhd2vl is Free (libre) Software:
//   Copyright (C) 2001 Vincenzo Liguori - Ocean Logic Pty Ltd
//     http://www.ocean-logic.com
//   Modifications Copyright (C) 2006 Mark Gonzales - PMC Sierra Inc
//   Modifications (C) 2010 Shankar Giri
//   Modifications Copyright (C) 2002, 2005, 2008-2010 Larry Doolittle - LBNL
//     http://doolittle.icarus.com/~larry/vhd2vl/
//
//   vhd2vl comes with ABSOLUTELY NO WARRANTY.  Always check the resulting
//   Verilog for correctness, ideally with a formal verification tool.
//
//   You are welcome to redistribute vhd2vl under certain conditions.
//   See the license (GPLv2) file included with the source for details.

// The result of translation follows.  Its copyright status should be
// considered unchanged from the original VHDL.

//------------------------------------------------------------------------------
//                                                                            --
//                          V H D L    F I L E                                --
//                          COPYRIGHT (C) 2006                                --
//                                                                            --
//------------------------------------------------------------------------------
//                                                                            --
// Title       : ZIGZAG                                                       --
// Design      : MDCT CORE                                                    --
// Author      : Michal Krepa                                                 --
//                                                                            --
//------------------------------------------------------------------------------
//                                                                            --
// File        : ZIGZAG.VHD                                                   --
// Created     : Sun Sep 3 2006                                               --
//                                                                            --
//------------------------------------------------------------------------------
//                                                                            --
//  Description : Zig-Zag scan                                                --
//                                                                            --
//------------------------------------------------------------------------------
// //////////////////////////////////////////////////////////////////////////////
// /// Copyright (c) 2013, Jahanzeb Ahmad
// /// All rights reserved.
// ///
// /// Redistribution and use in source and binary forms, with or without modification, 
// /// are permitted provided that the following conditions are met:
// ///
// ///  * Redistributions of source code must retain the above copyright notice, 
// ///    this list of conditions and the following disclaimer.
// ///  * Redistributions in binary form must reproduce the above copyright notice, 
// ///    this list of conditions and the following disclaimer in the documentation and/or 
// ///    other materials provided with the distribution.
// ///
// ///    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
// ///    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
// ///    OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
// ///    SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
// ///    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
// ///    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
// ///    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
// ///    WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
// ///    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
// ///   POSSIBILITY OF SUCH DAMAGE.
// ///
// ///
// ///  * http://opensource.org/licenses/MIT
// ///  * http://copyfree.org/licenses/mit/license.txt
// ///
// //////////////////////////////////////////////////////////////////////////////
//------------------------------------------------------------------------------
// no timescale needed

module ZIGZAG
#(
  parameter RAMADDR_W=6,
  parameter RAMDATA_W=12
)
(
 input wire 		       rst,
 input wire 		       clk,
 input wire [RAMDATA_W - 1:0]  di,
 input wire 		       divalid,
 input wire [5:0] 	       rd_addr,
 input wire 		       fifo_rden,
 output wire 		       fifo_empty,
 output wire [RAMDATA_W - 1:0] dout,
 output reg 		       dovalid,
 output reg [5:0] 	       zz_rd_addr
);
       
   // @todo: need to manually convert the ZIGZIG RAM'r
   //type ZIGZAG_TYPE is   array (0 to 2**RAMADDR_W-1) of INTEGER range 0 to 2**RAMADDR_W-1;
   //constant ZIGZAG_ARRAY : ZIGZAG_TYPE := 
   //                    (
   //                     0,1,8,16,9,2,3,10, 
   //                     17,24,32,25,18,11,4,5,
   //                     12,19,26,33,40,48,41,34,
   //                     27,20,13,6,7,14,21,28,
   //                     35,42,49,56,57,50,43,36,
   //                     29,22,15,23,30,37,44,51,
   //                     58,59,52,45,38,31,39,46,
   //                     53,60,61,54,47,55,62,63
   //                    );
   reg [5:0] ZIGZAG_ARRAY [0:64];
   initial begin
      ZIGZAG_ARRAY[0] = 0;    ZIGZAG_ARRAY[1] = 1;   ZIGZAG_ARRAY[2] = 8;   ZIGZAG_ARRAY[3] = 16;
      ZIGZAG_ARRAY[4] = 9;    ZIGZAG_ARRAY[5] = 2;   ZIGZAG_ARRAY[6] = 3;   ZIGZAG_ARRAY[7] = 10;

      ZIGZAG_ARRAY[8]  = 17;  ZIGZAG_ARRAY[9]  = 24; ZIGZAG_ARRAY[10] = 32; ZIGZAG_ARRAY[11] = 25;
      ZIGZAG_ARRAY[12] = 18;  ZIGZAG_ARRAY[13] = 11; ZIGZAG_ARRAY[14] = 4;  ZIGZAG_ARRAY[15] = 5;

      // @todo: ...
   end
   
   wire 		    fifo_wr;
   wire [11:0] 		    fifo_q;
   wire 		    fifo_full;
   wire [6:0] 		    fifo_count;
   wire [11:0] 		    fifo_data_in;
   wire 		    fifo_empty_s;
   
   assign dout = fifo_q;
   assign fifo_empty = fifo_empty_s;
   //-----------------------------------------------------------------
   // FIFO (show ahead)
   //-----------------------------------------------------------------
     FIFO
    #(.DATA_WIDTH(12),
      .ADDR_WIDTH(6)
      )
   U_FIFO
     (.rst(RST),
      .clk(CLK),
      .rinc(fifo_rden),
      .winc(fifo_wr),
      .datai(fifo_data_in),
      .datao(fifo_q),
      .fullo(fifo_full),
      .emptyo(fifo_empty_s),
      .count(fifo_count)
      );   
      
   //U_FIFO : entity work.FIFO   
   //generic map
   //(
   //      DATA_WIDTH        => 12,
   //      ADDR_WIDTH        => 6
   //)
   //port map 
   //(        
   //      rst               => RST,
   //      clk               => CLK,
   //      rinc              => fifo_rden,
   //      winc              => fifo_wr,
   //      datai             => fifo_data_in,
   //
   //      datao             => fifo_q,
   //      fullo             => fifo_full,
   //      emptyo            => fifo_empty_s,
   //      count             => fifo_count
   //);
   
   assign fifo_wr = divalid;
   assign fifo_data_in = di;
   always @(posedge clk) begin
      if(rst == 1'b 1) begin
	 zz_rd_addr <= {6{1'b0}};
      dovalid <= 1'b 0;
   end
      else begin
	 //
	 //zz_rd_addr <= std_logic_vector(
	 //              to_unsigned((ZIGZAG_ARRAY(to_integer(rd_addr))),6));
	 zz_rd_addr <= ZIGZAG_ARRAY[rd_addr];	 
	 dovalid <= fifo_rden &  ~fifo_empty_s;
      end
   end
   
   //------------------------------------------------------------------------------
   
endmodule
