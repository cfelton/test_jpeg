// File ../design/DCT1D_c.vhd translated with vhd2vl v2.4 VHDL to Verilog RTL translator
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
// Title       : DCT1D
// Design      : MDCT Core
// Author      : Michal Krepa
//
//------------------------------------------------------------------------------
//
// File        : DCT1D.VHD
// Created     : Sat Mar 5 7:37 2006
//
//------------------------------------------------------------------------------
//
//  Description : 1D Discrete Cosine Transform (1st stage)
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
//------------------------------------------------------------------------------
// ENTITY
//------------------------------------------------------------------------------
// no timescale needed

module DCT1D(
input wire clk,
input wire rst,
input wire [IP_W - 1:0] dcti,
input wire idv,
output wire odv,
output wire [OP_W - 1:0] dcto,
output wire [RAMADRR_W - 1:0] ramwaddro,
output wire [RAMDATA_W - 1:0] ramdatai,
output wire ramwe,
output wire wmemsel
);

// @todo: fix, manually convert
//romedatao    : in T_ROM1DATAO;
//romodatao    : in T_ROM1DATAO;
// @todo: fix, manually convert
//romeaddro    : out T_ROM1ADDRO;
//romoaddro    : out T_ROM1ADDRO;



//------------------------------------------------------------------------------
// ARCHITECTURE
//------------------------------------------------------------------------------
// @todo: manually convert

reg [IP_W:0] databuf_reg[N - 1:0];
reg [IP_W:0] latchbuf_reg[N - 1:0];
reg [RAMADRR_W / 2 - 1:0] col_reg = 0;
reg [RAMADRR_W / 2 - 1:0] row_reg = 0;
wire [RAMADRR_W / 2 - 1:0] rowr_reg = 0;
reg [RAMADRR_W / 2 - 1:0] inpcnt_reg = 0;
reg ramwe_s = 1'b 0;
reg wmemsel_reg = 1'b 0;
reg stage2_reg = 1'b 0;
reg [RAMADRR_W - 1:0] stage2_cnt_reg = 1;
reg [RAMADRR_W / 2 - 1:0] col_2_reg = 0;
reg [RAMADRR_W - 1:0] ramwaddro_s = 0;
reg even_not_odd = 1'b 0;
reg even_not_odd_d1 = 1'b 0;
reg even_not_odd_d2 = 1'b 0;
reg even_not_odd_d3 = 1'b 0;
reg ramwe_d1 = 1'b 0;
reg ramwe_d2 = 1'b 0;
reg ramwe_d3 = 1'b 0;
reg ramwe_d4 = 1'b 0;
reg [RAMADRR_W - 1:0] ramwaddro_d1 = 0;
reg [RAMADRR_W - 1:0] ramwaddro_d2 = 0;
reg [RAMADRR_W - 1:0] ramwaddro_d3 = 0;
reg [RAMADRR_W - 1:0] ramwaddro_d4 = 0;
reg wmemsel_d1 = 1'b 0;
reg wmemsel_d2 = 1'b 0;
reg wmemsel_d3 = 1'b 0;
reg wmemsel_d4 = 1'b 0;  // @todo: fix, manually convert
//signal romedatao_d1    : T_ROM1DATAO;
//signal romodatao_d1    : T_ROM1DATAO;
//signal romedatao_d2    : T_ROM1DATAO;
//signal romodatao_d2    : T_ROM1DATAO;
//signal romedatao_d3    : T_ROM1DATAO;
//signal romodatao_d3    : T_ROM1DATAO;
reg [DA_W - 1:0] dcto_1 = 0;
reg [DA_W - 1:0] dcto_2 = 0;
reg [DA_W - 1:0] dcto_3 = 0;
reg [DA_W - 1:0] dcto_4 = 0;

  assign ramwaddro = ramwaddro_d4;
  assign ramwe = ramwe_d4;
  assign ramdatai = dcto_4[DA_W - 1:12];
  assign wmemsel = wmemsel_d4;
  always @(posedge clk or posedge rst) begin
    if(rst == 1'b 1) begin
      inpcnt_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      // @todo: fix, manually convert
      //latchbuf_reg    <= (others => (others => '0')); 
      //databuf_reg     <= (others => (others => '0'));
      stage2_reg <= 1'b 0;
      stage2_cnt_reg <= {(((RAMADRR_W - 1))-((0))+1){1'b1}};
      ramwe_s <= 1'b 0;
      ramwaddro_s <= {(((RAMADRR_W - 1))-((0))+1){1'b0}};
      col_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      row_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      wmemsel_reg <= 1'b 0;
      col_2_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
    end else begin
      stage2_reg <= 1'b 0;
      ramwe_s <= 1'b 0;
      //------------------------------
      // 1st stage
      //------------------------------
      if(idv == 1'b 1) begin
        inpcnt_reg <= inpcnt_reg + 1;
        // right shift input data
        latchbuf_reg[N - 2:0] <= latchbuf_reg[N - 1:1];
        latchbuf_reg[N - 1] <= ({1'b 0,dcti}) - LEVEL_SHIFT;
        if(inpcnt_reg == (N - 1)) begin
          // after this sum databuf_reg is in range of -256 to 254 (min to max) 
          databuf_reg[0] <= latchbuf_reg[1] + ((({1'b 0,dcti}) - LEVEL_SHIFT));
          databuf_reg[1] <= latchbuf_reg[2] + latchbuf_reg[7];
          databuf_reg[2] <= latchbuf_reg[3] + latchbuf_reg[6];
          databuf_reg[3] <= latchbuf_reg[4] + latchbuf_reg[5];
          databuf_reg[4] <= latchbuf_reg[1] - ((({1'b 0,dcti}) - LEVEL_SHIFT));
          databuf_reg[5] <= latchbuf_reg[2] - latchbuf_reg[7];
          databuf_reg[6] <= latchbuf_reg[3] - latchbuf_reg[6];
          databuf_reg[7] <= latchbuf_reg[4] - latchbuf_reg[5];
          stage2_reg <= 1'b 1;
        end
      end
      //------------------------------
      //------------------------------
      // 2nd stage
      //------------------------------
      if(stage2_cnt_reg < N) begin
        stage2_cnt_reg <= stage2_cnt_reg + 1;
        // write RAM
        ramwe_s <= 1'b 1;
        // reverse col/row order for transposition purpose
        ramwaddro_s <= {col_2_reg,row_reg};
        // increment column counter
        col_reg <= col_reg + 1;
        col_2_reg <= col_2_reg + 1;
        // finished processing one input row
        if(col_reg == 0) begin
          row_reg <= row_reg + 1;
          // switch to 2nd memory
          if(row_reg == (N - 1)) begin
            wmemsel_reg <=  ~wmemsel_reg;
            col_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
          end
        end
      end
      if(stage2_reg == 1'b 1) begin
        stage2_cnt_reg <= {(((RAMADRR_W - 1))-((0))+1){1'b0}};
        // @todo: fix, manually convert
        //col_reg        <= (0=>'1',others => '0');
        col_2_reg <= {(((RAMADRR_W / 2 - 1))-((0))+1){1'b0}};
      end
      //--------------------------------   
    end
  end

  // output data pipeline
  always @(posedge CLK or posedge RST) begin
    if(RST == 1'b 1) begin
      even_not_odd <= 1'b 0;
      even_not_odd_d1 <= 1'b 0;
      even_not_odd_d2 <= 1'b 0;
      even_not_odd_d3 <= 1'b 0;
      ramwe_d1 <= 1'b 0;
      ramwe_d2 <= 1'b 0;
      ramwe_d3 <= 1'b 0;
      ramwe_d4 <= 1'b 0;
      ramwaddro_d1 <= {(((RAMADRR_W - 1))-((0))+1){1'b0}};
      ramwaddro_d2 <= {(((RAMADRR_W - 1))-((0))+1){1'b0}};
      ramwaddro_d3 <= {(((RAMADRR_W - 1))-((0))+1){1'b0}};
      ramwaddro_d4 <= {(((RAMADRR_W - 1))-((0))+1){1'b0}};
      wmemsel_d1 <= 1'b 0;
      wmemsel_d2 <= 1'b 0;
      wmemsel_d3 <= 1'b 0;
      wmemsel_d4 <= 1'b 0;
      dcto_1 <= {(((DA_W - 1))-((0))+1){1'b0}};
      dcto_2 <= {(((DA_W - 1))-((0))+1){1'b0}};
      dcto_3 <= {(((DA_W - 1))-((0))+1){1'b0}};
      dcto_4 <= {(((DA_W - 1))-((0))+1){1'b0}};
    end else begin
      even_not_odd <= stage2_cnt_reg[0];
      even_not_odd_d1 <= even_not_odd;
      even_not_odd_d2 <= even_not_odd_d1;
      even_not_odd_d3 <= even_not_odd_d2;
      ramwe_d1 <= ramwe_s;
      ramwe_d2 <= ramwe_d1;
      ramwe_d3 <= ramwe_d2;
      ramwe_d4 <= ramwe_d3;
      ramwaddro_d1 <= ramwaddro_s;
      ramwaddro_d2 <= ramwaddro_d1;
      ramwaddro_d3 <= ramwaddro_d2;
      ramwaddro_d4 <= ramwaddro_d3;
      wmemsel_d1 <= wmemsel_reg;
      wmemsel_d2 <= wmemsel_d1;
      wmemsel_d3 <= wmemsel_d2;
      wmemsel_d4 <= wmemsel_d3;
      // @todo: fix, manually convert
      //if even_not_odd = '0' then
      //  -- @todo: fix, manually convert
      //  dcto_1 <= STD_LOGIC_VECTOR(RESIZE
      //    (RESIZE(SIGNED(romedatao(0)),DA_W) + 
      //    (RESIZE(SIGNED(romedatao(1)),DA_W-1) & '0') +
      //    (RESIZE(SIGNED(romedatao(2)),DA_W-2) & "00"),
      //    DA_W));
      //else
      //  dcto_1 <= STD_LOGIC_VECTOR(RESIZE
      //    (RESIZE(SIGNED(romodatao(0)),DA_W) + 
      //    (RESIZE(SIGNED(romodatao(1)),DA_W-1) & '0') +
      //    (RESIZE(SIGNED(romodatao(2)),DA_W-2) & "00"),
      //    DA_W));
      //end if;
      //
      //if even_not_odd_d1 = '0' then
      //  dcto_2 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_1) +
      //    (RESIZE(SIGNED(romedatao_d1(3)),DA_W-3) & "000") +
      //    (RESIZE(SIGNED(romedatao_d1(4)),DA_W-4) & "0000"),
      //    DA_W));
      //else
      //  dcto_2 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_1) + 
      //    (RESIZE(SIGNED(romodatao_d1(3)),DA_W-3) & "000") +
      //    (RESIZE(SIGNED(romodatao_d1(4)),DA_W-4) & "0000"),
      //    DA_W));
      //end if;
      //
      //if even_not_odd_d2 = '0' then
      //  dcto_3 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_2) +
      //    (RESIZE(SIGNED(romedatao_d2(5)),DA_W-5) & "00000") +
      //    (RESIZE(SIGNED(romedatao_d2(6)),DA_W-6) & "000000"),
      //    DA_W));
      //else
      //  dcto_3 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_2) + 
      //    (RESIZE(SIGNED(romodatao_d2(5)),DA_W-5) & "00000") +
      //    (RESIZE(SIGNED(romodatao_d2(6)),DA_W-6) & "000000"),
      //    DA_W));
      //end if;
      //
      //if even_not_odd_d3 = '0' then
      //  dcto_4 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_3) +
      //    (RESIZE(SIGNED(romedatao_d3(7)),DA_W-7) & "0000000") -
      //    (RESIZE(SIGNED(romedatao_d3(8)),DA_W-8) & "00000000"),
      //    DA_W));
      //else
      //  dcto_4 <= STD_LOGIC_VECTOR(RESIZE
      //    (signed(dcto_3) + 
      //    (RESIZE(SIGNED(romodatao_d3(7)),DA_W-7) & "0000000") -
      //    (RESIZE(SIGNED(romodatao_d3(8)),DA_W-8) & "00000000"),
      //    DA_W));
      //end if;
    end
  end

    // @todo: fix, manually convert
  // read precomputed MAC results from LUT
  //p_romaddr : process(CLK, RST)
  //begin
  //  if RST = '1' then
  //    romeaddro   <= (others => (others => '0')); 
  //    romoaddro   <= (others => (others => '0')); 
  //  elsif CLK'event and CLK = '1' then
  //    for i in 0 to 8 loop
  //      -- even
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
  //p_romdatao_d1 : process(CLK, RST)
  //begin
  //  if RST = '1' then
  //    romedatao_d1    <= (others => (others => '0'));
  //    romodatao_d1    <= (others => (others => '0'));
  //    romedatao_d2    <= (others => (others => '0'));
  //    romodatao_d2    <= (others => (others => '0'));
  //    romedatao_d3    <= (others => (others => '0'));
  //    romodatao_d3    <= (others => (others => '0'));
  //  elsif CLK'event and CLK = '1' then
  //    romedatao_d1   <= romedatao;
  //    romodatao_d1   <= romodatao;
  //    romedatao_d2   <= romedatao_d1;
  //    romodatao_d2   <= romodatao_d1;
  //    romedatao_d3   <= romedatao_d2;
  //    romodatao_d3   <= romodatao_d2;
  //  end if;
  //end process;
//------------------------------------------------------------------------------

endmodule
