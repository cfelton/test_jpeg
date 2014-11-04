// File ../design/DCT2D_c.VHD translated with vhd2vl v2.4 VHDL to Verilog RTL translator
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
//                          COPYRIGHT (C) 2006                                --
//                                                                            --
//------------------------------------------------------------------------------
//
// Title       : DCT2D
// Design      : MDCT Core
// Author      : Michal Krepa
//
//------------------------------------------------------------------------------
//
// File        : DCT2D.VHD
// Created     : Sat Mar 28 22:32 2006
//
//------------------------------------------------------------------------------
//
//  Description : 1D Discrete Cosine Transform (second stage)
//
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
// no timescale needed

module DCT2D(
input wire clk,
input wire rst,
input wire [RAMDATA_W - 1:0] ramdatao,
input wire dataready,
output wire odv,
output wire [OP_W - 1:0] dcto,
output wire [RAMADRR_W - 1:0] ramraddro,
output wire rmemsel,
output reg datareadyack
);

// @todo: manually convert
//romedatao    : in T_ROM2DATAO;
//romodatao    : in T_ROM2DATAO;
// @todo: manually convert
//romeaddro    : out T_ROM2ADDRO;
//romoaddro    : out T_ROM2ADDRO;




wire [RAMDATA_W:0] databuf_reg[N - 1:0];
wire [RAMDATA_W:0] latchbuf_reg[N - 1:0];
reg [RAMADRR_W / 2 - 1:0] col_reg = 0;
reg [RAMADRR_W / 2 - 1:0] row_reg = 0;
reg [RAMADRR_W / 2 - 1:0] colram_reg = 0;
reg [RAMADRR_W / 2 - 1:0] rowram_reg = 0;
reg [RAMADRR_W / 2 - 1:0] colr_reg = 0;
reg [RAMADRR_W / 2 - 1:0] rowr_reg = 0;
reg rmemsel_reg = 1'b 0;
reg stage1_reg = 1'b 0;
reg stage2_reg = 1'b 0;
reg [RAMADRR_W - 1:0] stage2_cnt_reg = 1;
reg dataready_2_reg = 1'b 0;
reg even_not_odd = 1'b 0;
reg even_not_odd_d1 = 1'b 0;
reg even_not_odd_d2 = 1'b 0;
reg even_not_odd_d3 = 1'b 0;
reg even_not_odd_d4 = 1'b 0;
reg odv_d0 = 1'b 0;
reg odv_d1 = 1'b 0;
reg odv_d2 = 1'b 0;
reg odv_d3 = 1'b 0;
reg odv_d4 = 1'b 0;
reg odv_d5 = 1'b 0;
reg [DA2_W - 1:0] dcto_1 = 0;
reg [DA2_W - 1:0] dcto_2 = 0;
reg [DA2_W - 1:0] dcto_3 = 0;
reg [DA2_W - 1:0] dcto_4 = 0;
reg [DA2_W - 1:0] dcto_5 = 0;  // @todo: fix, manually convert
//signal romedatao_d1    : T_ROM2DATAO;
//signal romodatao_d1    : T_ROM2DATAO;
//signal romedatao_d2    : T_ROM2DATAO;
//signal romodatao_d2    : T_ROM2DATAO;
//signal romedatao_d3    : T_ROM2DATAO;
//signal romodatao_d3    : T_ROM2DATAO;
//signal romedatao_d4    : T_ROM2DATAO;
//signal romodatao_d4    : T_ROM2DATAO;

  // @todo: fix, manually convert
  //ramraddro_sg:
  //ramraddro  <= STD_LOGIC_VECTOR(rowr_reg & colr_reg);  
  //rmemsel_sg:
  //rmemsel    <= rmemsel_reg;
  always @(posedge clk or posedge rst) begin
    if(rst == 1'b 1) begin
      stage2_cnt_reg <= {(((RAMADRR_W - 1))-((0))+1){1'b1}};
      rmemsel_reg <= 1'b 0;
      stage1_reg <= 1'b 0;
      stage2_reg <= 1'b 0;
      colram_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      rowram_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      col_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      row_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      // @todo: fix, manually convert
      //latchbuf_reg         <= (others => (others => '0')); 
      //databuf_reg          <= (others => (others => '0'));
      odv_d0 <= 1'b 0;
      colr_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      rowr_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      dataready_2_reg <= 1'b 0;
    end else begin
      stage2_reg <= 1'b 0;
      odv_d0 <= 1'b 0;
      datareadyack <= 1'b 0;
      dataready_2_reg <= dataready;
      //--------------------------------
      // read DCT 1D to barrel shifer
      //--------------------------------
      if(stage1_reg == 1'b 1) begin
        // @todo: fix, manually convert
        // -- right shift input data
        // latchbuf_reg(N-2 downto 0) <= latchbuf_reg(N-1 downto 1);
        // latchbuf_reg(N-1)          <= RESIZE(SIGNED(ramdatao),RAMDATA_W+1);       
        colram_reg <= colram_reg + 1;
        colr_reg <= colr_reg + 1;
        if(colram_reg == (N - 2)) begin
          rowr_reg <= rowr_reg + 1;
        end
        if(colram_reg == (N - 1)) begin
          rowram_reg <= rowram_reg + 1;
          if(rowram_reg == (N - 1)) begin
            stage1_reg <= 1'b 0;
            colr_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
            // release memory
            rmemsel_reg <=  ~rmemsel_reg;
          end
          // @todo: fix, manually convert
          //-- after this sum databuf_reg is in range of -256 to 254 (min to max) 
          //databuf_reg(0)  <= latchbuf_reg(1)+RESIZE(SIGNED(ramdatao),RAMDATA_W+1);
          //databuf_reg(1)  <= latchbuf_reg(2)+latchbuf_reg(7);
          //databuf_reg(2)  <= latchbuf_reg(3)+latchbuf_reg(6);
          //databuf_reg(3)  <= latchbuf_reg(4)+latchbuf_reg(5);
          //databuf_reg(4)  <= latchbuf_reg(1)-RESIZE(SIGNED(ramdatao),RAMDATA_W+1);
          //databuf_reg(5)  <= latchbuf_reg(2)-latchbuf_reg(7);
          //databuf_reg(6)  <= latchbuf_reg(3)-latchbuf_reg(6);
          //databuf_reg(7)  <= latchbuf_reg(4)-latchbuf_reg(5);
          // 8 point input latched
          stage2_reg <= 1'b 1;
        end
      end
      //------------------------------
      // 2nd stage
      //------------------------------
      if(stage2_cnt_reg < N) begin
        stage2_cnt_reg <= stage2_cnt_reg + 1;
        // output data valid
        odv_d0 <= 1'b 1;
        // increment column counter
        col_reg <= col_reg + 1;
        // finished processing one input row
        if(col_reg == (N - 1)) begin
          row_reg <= row_reg + 1;
        end
      end
      if(stage2_reg == 1'b 1) begin
        stage2_cnt_reg <= {(((RAMADRR_W - 1))-((0))+1){1'b0}};
        // @todo: fix, manually convert
        //col_reg        <= (0=>'1',others => '0');
      end
      //------------------------------
      //--------------------------------
      // wait for new data
      //--------------------------------
      // one of ram buffers has new data, process it
      if(dataready == 1'b 1 && dataready_2_reg == 1'b 0) begin
        stage1_reg <= 1'b 1;
        // to account for 1T RAM delay, increment RAM address counter
        colram_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
        // @todo: fix, manually convert
        //colr_reg      <= (0=>'1',others => '0');
        datareadyack <= 1'b 1;
      end
      //--------------------------------
    end
  end

  always @(posedge CLK or posedge RST) begin
    if(RST == 1'b 1) begin
      even_not_odd <= 1'b 0;
      even_not_odd_d1 <= 1'b 0;
      even_not_odd_d2 <= 1'b 0;
      even_not_odd_d3 <= 1'b 0;
      even_not_odd_d4 <= 1'b 0;
      odv_d1 <= 1'b 0;
      odv_d2 <= 1'b 0;
      odv_d3 <= 1'b 0;
      odv_d4 <= 1'b 0;
      odv_d5 <= 1'b 0;
      dcto_1 <= {(((DA2_W - 1))-((0))+1){1'b0}};
      dcto_2 <= {(((DA2_W - 1))-((0))+1){1'b0}};
      dcto_3 <= {(((DA2_W - 1))-((0))+1){1'b0}};
      dcto_4 <= {(((DA2_W - 1))-((0))+1){1'b0}};
      dcto_5 <= {(((DA2_W - 1))-((0))+1){1'b0}};
    end else begin
      even_not_odd <= stage2_cnt_reg[0];
      even_not_odd_d1 <= even_not_odd;
      even_not_odd_d2 <= even_not_odd_d1;
      even_not_odd_d3 <= even_not_odd_d2;
      even_not_odd_d4 <= even_not_odd_d3;
      odv_d1 <= odv_d0;
      odv_d2 <= odv_d1;
      odv_d3 <= odv_d2;
      odv_d4 <= odv_d3;
      odv_d5 <= odv_d4;
      // @todo: fix, manually convert
      //if even_not_odd = '0' then
      //  dcto_1 <= STD_LOGIC_VECTOR(RESIZE
      //    (RESIZE(SIGNED(romedatao(0)),DA2_W) + 
      //    (RESIZE(SIGNED(romedatao(1)),DA2_W-1) & '0') +
      //    (RESIZE(SIGNED(romedatao(2)),DA2_W-2) & "00"),
      //    DA2_W));
      //else
      //  dcto_1 <= STD_LOGIC_VECTOR(RESIZE
      //    (RESIZE(SIGNED(romodatao(0)),DA2_W) + 
      //    (RESIZE(SIGNED(romodatao(1)),DA2_W-1) & '0') +
      //    (RESIZE(SIGNED(romodatao(2)),DA2_W-2) & "00"),
      //    DA2_W));
      //end if;
      //
      //if even_not_odd_d1 = '0' then
      //  dcto_2 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_1) + 
      //    (RESIZE(SIGNED(romedatao_d1(3)),DA2_W-3) & "000") +
      //    (RESIZE(SIGNED(romedatao_d1(4)),DA2_W-4) & "0000"),
      //    DA2_W));
      //else
      //  dcto_2 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_1) + 
      //    (RESIZE(SIGNED(romodatao_d1(3)),DA2_W-3) & "000") +
      //    (RESIZE(SIGNED(romodatao_d1(4)),DA2_W-4) & "0000"),
      //    DA2_W)); 
      //end if;
      //
      //if even_not_odd_d2 = '0' then
      //  dcto_3 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_2) + 
      //    (RESIZE(SIGNED(romedatao_d2(5)),DA2_W-5) & "00000") +
      //    (RESIZE(SIGNED(romedatao_d2(6)),DA2_W-6) & "000000"),
      //    DA2_W));
      //else
      //  dcto_3 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_2) + 
      //    (RESIZE(SIGNED(romodatao_d2(5)),DA2_W-5) & "00000") +
      //    (RESIZE(SIGNED(romodatao_d2(6)),DA2_W-6) & "000000"),
      //    DA2_W)); 
      //end if;
      //
      //if even_not_odd_d3 = '0' then
      //  dcto_4 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_3) +
      //    (RESIZE(SIGNED(romedatao_d3(7)),DA2_W-7) & "0000000") +
      //    (RESIZE(SIGNED(romedatao_d3(8)),DA2_W-8) & "00000000"),
      //    DA2_W));
      //else
      //  dcto_4 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_3) + 
      //    (RESIZE(SIGNED(romodatao_d3(7)),DA2_W-7) & "0000000") +
      //    (RESIZE(SIGNED(romodatao_d3(8)),DA2_W-8) & "00000000"),
      //    DA2_W)); 
      //end if;
      //
      //if even_not_odd_d4 = '0' then
      //  dcto_5 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_4) +
      //    (RESIZE(SIGNED(romedatao_d4(9)),DA2_W-9) & "000000000") -
      //    (RESIZE(SIGNED(romedatao_d4(10)),DA2_W-10) & "0000000000"),
      //    DA2_W));
      //else
      //  dcto_5 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_4) + 
      //    (RESIZE(SIGNED(romodatao_d4(9)),DA2_W-9) & "000000000") -
      //    (RESIZE(SIGNED(romodatao_d4(10)),DA2_W-10) & "0000000000"),
      //    DA2_W)); 
      //end if;
      // end manual conversion
    end
  end

  assign dcto = dcto_5[DA2_W - 1:12];
  assign odv = odv_d5;
    // @todo: fix, manually convert
  //p_romaddr : process(CLK, RST)
  //begin
  //  if RST = '1' then
  //    romeaddro   <= (others => (others => '0')); 
  //    romoaddro   <= (others => (others => '0')); 
  //  elsif CLK'event and CLK = '1' then
  //    for i in 0 to 10 loop
  //      -- read precomputed MAC results from LUT
  //      romeaddro(i) <= STD_LOGIC_VECTOR(col_reg(RAMADRR_W/2-1 downto 1)) & 
  //               databuf_reg(0)(i) & 
  //               databuf_reg(1)(i) &
  //               databuf_reg(2)(i) &
  //               databuf_reg(3)(i);
  //      -- odd
  //      romoaddro(i) <= STD_LOGIC_VECTOR(col_reg(RAMADRR_W/2-1 downto 1)) & 
  //               databuf_reg(4)(i) & 
  //               databuf_reg(5)(i) &
  //               databuf_reg(6)(i) &
  //               databuf_reg(7)(i);
  //    end loop;
  //  end if;
  //end process;
  //
  //p_romdatao_dly : process(CLK, RST)
  //begin
  //  if RST = '1' then
  //    romedatao_d1    <= (others => (others => '0'));       
  //    romodatao_d1    <= (others => (others => '0'));
  //    romedatao_d2    <= (others => (others => '0'));       
  //    romodatao_d2    <= (others => (others => '0'));
  //    romedatao_d3    <= (others => (others => '0'));       
  //    romodatao_d3    <= (others => (others => '0'));
  //    romedatao_d4    <= (others => (others => '0'));       
  //    romodatao_d4    <= (others => (others => '0'));
  //  elsif CLK'event and CLK = '1' then
  //    romedatao_d1   <= romedatao;
  //    romodatao_d1   <= romodatao;
  //    romedatao_d2   <= romedatao_d1;
  //    romodatao_d2   <= romodatao_d1;
  //    romedatao_d3   <= romedatao_d2;
  //    romodatao_d3   <= romodatao_d2;
  //    romedatao_d4   <= romedatao_d3;
  //    romodatao_d4   <= romodatao_d3;
  //  end if;
  //end process;
  // end manual conversion
//------------------------------------------------------------------------------

endmodule
