// File ../design/QUANTIZER_c.vhd translated with vhd2vl v2.4 VHDL to Verilog RTL translator
// vhd2vl settings:
//  * Verilog Module Declaration Style: 2001

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
//                          COPYRIGHT (C) 2006-2009                           --
//                                                                            --
//------------------------------------------------------------------------------
//                                                                            --
// Title       : DIVIDER                                                      --
// Design      : DCT QUANTIZER                                                --
// Author      : Michal Krepa                                                 --
//                                                                            --
//------------------------------------------------------------------------------
//                                                                            --
// File        : QUANTIZER.VHD                                                --
// Created     : Sun Aug 27 2006                                              --
//                                                                            --
//------------------------------------------------------------------------------
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

module quantizer(
input wire rst,
input wire clk,
input wire [SIZE_C - 1:0] di,
input wire divalid,
input wire [7:0] qdata,
input wire [6:0] qwaddr,
input wire qwren,
input wire [2:0] cmp_idx,
output wire [SIZE_C - 1:0] do,
output wire dovalid
);

parameter [31:0] SIZE_C=12;
parameter [31:0] RAMQADDR_W=7;
parameter [31:0] RAMQDATA_W=8;



parameter INTERN_PIPE_C = 3;
reg [RAMQADDR_W - 2:0] romaddr_s = 0;
wire [RAMQADDR_W - 1:0] slv_romaddr_s = 0;
wire [RAMQDATA_W - 1:0] romdatao_s = 0;
wire [SIZE_C - 1:0] divisor_s = 0;
wire [SIZE_C - 1:0] remainder_s = 0;
wire [SIZE_C - 1:0] do_s = 0;
wire round_s = 1'b 0;
reg [SIZE_C - 1:0] di_d1 = 0;
reg [4:0] pipeline_reg = 0;
reg [SIZE_C + INTERN_PIPE_C + 1 - 1:0] sign_bit_pipe = 0;
wire [SIZE_C - 1:0] do_rdiv = 0;
reg table_select = 1'b 0;

  //--------------------------
  // RAMQ
  //--------------------------
  // @todo manually instantiate
  //U_RAMQ : entity work.RAMZ
  //  generic map
  //  (
  //    RAMADDR_W    => RAMQADDR_W,
  //    RAMDATA_W    => RAMQDATA_W
  //  )
  //  port map
  //  (
  //    d           => qdata,
  //    waddr       => qwaddr,
  //    raddr       => slv_romaddr_s,
  //    we          => qwren,
  //    clk         => CLK,
  //                
  //    q           => romdatao_s
  //  );
  assign divisor_s[RAMQDATA_W - 1:0] = romdatao_s;
  assign divisor_s[SIZE_C - 1:RAMQDATA_W] = {(((SIZE_C - 1))-((RAMQDATA_W))+1){1'b0}};
  // @todo manually instantiate
  //r_divider : entity work.r_divider
  //port map
  //(
  //     rst   => rst,
  //     clk   => clk,
  //     a     => di_d1,     
  //     d     => romdatao_s,    
  //           
  //     q     => do_s
  //) ;
  assign do = do_s;
  assign slv_romaddr_s = {table_select,(romaddr_s)};
  //----------------------------
  // Quantization sub table select
  //----------------------------
  always @(posedge clk) begin
    if(rst == 1'b 1) begin
      table_select <= 1'b 0;
    end
    else begin
      // luminance table select
      if(cmp_idx < 2) begin
        table_select <= 1'b 0;
        // chrominance table select
      end
      else begin
        table_select <= 1'b 1;
      end
    end
  end

  //--------------------------
  // address incrementer
  //--------------------------
  always @(posedge clk) begin
    if(rst == 1'b 1) begin
      romaddr_s <= {(((RAMQADDR_W - 2))-((0))+1){1'b0}};
      pipeline_reg <= {5{1'b0}};
      di_d1 <= {(((SIZE_C - 1))-((0))+1){1'b0}};
      sign_bit_pipe <= {(((SIZE_C + INTERN_PIPE_C + 1 - 1))-((0))+1){1'b0}};
    end
    else begin
      if(divalid == 1'b 1) begin
        // @todo fix
        //romaddr_s <= romaddr_s + TO_UNSIGNED(1,romaddr_s'length);
      end
      //pipeline_reg <= pipeline_reg(pipeline_reg'length-2 downto 0) & divalid;
      pipeline_reg <= {pipeline_reg[5 - 2:0],divalid};
      di_d1 <= di;
      // @todo fix the following
      // sign_bit_pipe <= sign_bit_pipe(sign_bit_pipe'length-2 downto 0) & di(SIZE_C-1);
    end
  end

  // @todo: fix
  assign dovalid = pipeline_reg[4];
//------------------------------------------------------------------------------

endmodule
