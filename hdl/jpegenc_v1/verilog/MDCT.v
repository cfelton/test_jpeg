// File ../design/MDCT_c.VHD translated with vhd2vl v2.4 VHDL to Verilog RTL translator
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
//
// Title       : DCT
// Design      : MDCT Core
// Author      : Michal Krepa
// Company     : None
//
//------------------------------------------------------------------------------
//
// File        : MDCT.VHD
// Created     : Sat Feb 25 16:12 2006
//
//------------------------------------------------------------------------------
//
//  Description : Discrete Cosine Transform - chip top level (w/ memories)
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

module MDCT
#(
  parameter IP_W        = 8,  
  parameter OP_W        = 12,
  parameter N           = 8,
  parameter COE_W       = 12,
  parameter ROMDATA_W   = COE_W+2,
  parameter ROMADDR_W   = 6,
  parameter RAMDATA_W   = 10,  
  parameter RAMADRR_W   = 6,
  parameter LEVEL_SHIFT = 128,
  parameter DA_W        = ROMDATA_W+IP_W

)  
(
 input wire 		   clk,
 input wire 		   rst,
 input wire [IP_W - 1:0]   dcti,
 input wire 		   idv,
 output wire 		   odv,
 output wire [COE_W - 1:0] dcto,
 output wire 		   odv1,
 output wire [OP_W - 1:0]  dcto1
);
    
    // debug
    
    wire [RAMDATA_W - 1:0] ramdatao_s;
    wire [RAMADRR_W - 1:0] ramraddro_s;
    wire [RAMADRR_W - 1:0] ramwaddro_s;
    wire [RAMDATA_W - 1:0] ramdatai_s;
    wire 		   ramwe_s;  

    // @todo: fix, converter doesn't handle user defined types
    
    //signal romedatao_s          : T_ROM1DATAO;
    //signal romodatao_s          : T_ROM1DATAO;
    //signal romeaddro_s          : T_ROM1ADDRO;
    //signal romoaddro_s          : T_ROM1ADDRO;
    //
    //signal rome2datao_s         : T_ROM2DATAO;
    //signal romo2datao_s         : T_ROM2DATAO;
    //signal rome2addro_s         : T_ROM2ADDRO;
    //signal romo2addro_s         : T_ROM2ADDRO;
    
    wire 		   odv2_s;
    wire [OP_W - 1:0] 	   dcto2_s;
    wire 		   trigger2_s;
    wire 		   trigger1_s;
    wire [RAMDATA_W - 1:0] ramdatao1_s;
    wire [RAMDATA_W - 1:0] ramdatao2_s;
    wire 		   ramwe1_s;
    wire 		   ramwe2_s;
    wire 		   memswitchrd_s;
    wire 		   memswitchwr_s;
    wire 		   wmemsel_s;
    wire 		   rmemsel_s;
    wire 		   dataready_s;
    wire 		   datareadyack_s;

  //----------------------------
  // 1D DCT port map
  //----------------------------
  // @todo: fix, manually instantiate
  //U_DCT1D : entity work.DCT1D
  //  port map(       
  //      clk          => clk,         
  //      rst          => rst,      
  //      dcti         => dcti,   
  //      idv          => idv,
  //      romedatao    => romedatao_s,
  //      romodatao    => romodatao_s,
  //  
  //      odv          => odv1,
  //      dcto         => dcto1,
  //      romeaddro    => romeaddro_s,
  //      romoaddro    => romoaddro_s,
  //      ramwaddro    => ramwaddro_s,
  //      ramdatai     => ramdatai_s,
  //      ramwe        => ramwe_s,
  //      wmemsel      => wmemsel_s
  //                );
  //----------------------------
  // 1D DCT port map
  //----------------------------
  // @todo: fix, manually instantiate  
  //U_DCT2D : entity work.DCT2D
  //  port map(       
  //      clk          => clk,         
  //      rst          => rst,      
  //      romedatao    => rome2datao_s,
  //      romodatao    => romo2datao_s,
  //      ramdatao     => ramdatao_s,
  //      dataready    => dataready_s,  
  //    
  //      odv          => odv,
  //      dcto         => dcto,
  //      romeaddro    => rome2addro_s,
  //      romoaddro    => romo2addro_s,
  //      ramraddro    => ramraddro_s,
  //      rmemsel      => rmemsel_s,
  //      datareadyack => datareadyack_s
  //                );
  //----------------------------
  // RAM1 port map
  //----------------------------
  // @todo: fix, manually instantiate
  //U1_RAM : entity work.RAM   
  //  port map (      
  //        d          => ramdatai_s,               
  //        waddr      => ramwaddro_s,     
  //        raddr      => ramraddro_s,     
  //        we         => ramwe1_s,     
  //        clk        => clk,      
  //        
  //        q          => ramdatao1_s      
  //  );
  //----------------------------
  // RAM2 port map
  //----------------------------
  // @todo: fix, manually instantiate
  //U2_RAM : entity work.RAM   
  //  port map (      
  //        d          => ramdatai_s,               
  //        waddr      => ramwaddro_s,     
  //        raddr      => ramraddro_s,     
  //        we         => ramwe2_s,     
  //        clk        => clk,      
  //        
  //        q          => ramdatao2_s      
  //  );
  // double buffer switch
  assign ramwe1_s = memswitchwr_s == 1'b 0 ? ramwe_s : 1'b 0;
  assign ramwe2_s = memswitchwr_s == 1'b 1 ? ramwe_s : 1'b 0;
  assign ramdatao_s = memswitchrd_s == 1'b 0 ? ramdatao1_s : ramdatao2_s;
    //----------------------------
  // DBUFCTL
  //----------------------------
  // @todo: fix, manually instantiate
  //U_DBUFCTL : entity work.DBUFCTL         
  //        port map(         
  //                clk            => clk,
  //                rst            => rst,
  //    wmemsel        => wmemsel_s,
  //    rmemsel        => rmemsel_s,
  //    datareadyack   => datareadyack_s,
  //      
  //    memswitchwr    => memswitchwr_s,
  //    memswitchrd    => memswitchrd_s,
  //    dataready      => dataready_s
  //                );  
  //----------------------------
  // 1st stage ROMs
  //----------------------------
  // @todo: fix, manually instantiate
  //G_ROM_ST1 : for i in 0 to 8 generate
  //  U1_ROME : entity work.ROME 
  //  port map( 
  //       addr        => romeaddro_s(i), 
  //       clk         => clk,   
  //       
  //       datao       => romedatao_s(i)
  //  );
  //  
  //  U1_ROMO : entity work.ROMO 
  //  port map( 
  //       addr        => romoaddro_s(i), 
  //       clk         => clk,   
  //       
  //       datao       => romodatao_s(i)
  //  );
  //end generate G_ROM_ST1;
  //----------------------------
  // 2nd stage ROMs
  //----------------------------
  // @todo: fix, manually instantiate
  //G_ROM_ST2 : for i in 0 to 10 generate
  //  U2_ROME : entity work.ROME 
  //  port map( 
  //       addr        => rome2addro_s(i), 
  //       clk         => clk,   
  //       
  //       datao       => rome2datao_s(i)
  //  );
  //  
  //  U2_ROMO : entity work.ROMO 
  //  port map( 
  //       addr        => romo2addro_s(i), 
  //       clk         => clk,   
  //       
  //       datao       => romo2datao_s(i)
  //  );
  //
  //end generate G_ROM_ST2;

endmodule
