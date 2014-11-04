// File ../design/CtrlSM_c.vhd translated with vhd2vl v2.4 VHDL to Verilog RTL translator
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

//-----------------------------------------------------------------------------
// File Name :  CtrlSM.vhd
//
// Project   : JPEG_ENC
//
// Module    : CtrlSM
//
// Content   : CtrlSM
//
// Description : CtrlSM core
//
// Spec.     : 
//
// Author    : Michal Krepa
//
//-----------------------------------------------------------------------------
// History :
// 20090301: (MK): Initial Creation.
//-----------------------------------------------------------------------------
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
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
//--------------------------------- LIBRARY/PACKAGE ---------------------------
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
// generic packages/libraries:
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
// user packages/libraries:
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
//--------------------------------- ENTITY ------------------------------------
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
// no timescale needed

module CtrlSM
//#(
//)  
(
 input wire 	   CLK,
 input wire 	   RST,
 input wire 	   outif_almost_full,
 input wire 	   sof,
 input wire [15:0] img_size_x,
 input wire [15:0] img_size_y,
 output reg 	   jpeg_ready,
 output reg 	   jpeg_busy,
 output wire 	   fdct_start,
 input wire 	   fdct_ready,
 output wire 	   zig_start,
 input wire 	   zig_ready,
 output wire 	   qua_start,
 input wire 	   qua_ready,
 output wire 	   rle_start,
 input wire 	   rle_ready,
 output wire 	   huf_start,
 input wire 	   huf_ready,
 output wire 	   bs_start,
 input wire 	   bs_ready,
 output reg 	   jfif_start,
 input wire 	   jfif_ready,
 output reg 	   jfif_eoi,
 output reg 	   out_mux_ctrl
);

    // output IF
    // HOST IF
    // FDCT
    //fdct_sm_settings   : out T_SM_SETTINGS;
    // ZIGZAG
    //zig_sm_settings    : out T_SM_SETTINGS;
    // Quantizer
    //qua_sm_settings    : out T_SM_SETTINGS;
    // RLE
    //rle_sm_settings    : out T_SM_SETTINGS;
    // Huffman
    //huf_sm_settings    : out T_SM_SETTINGS;
    // ByteStuffdr
    //bs_sm_settings     : out T_SM_SETTINGS;
    // JFIF GEN
    // OUT MUX
    
    // @todo: check, VHDL used global values from the package
    //    need to verify these are correct
    localparam NUM_STAGES = 6;
    localparam CMP_MAX = 4;
			 
    
    // @todo: manually fix
    //type T_ARR_SM_SETTINGS is array(NUM_STAGES+1 downto 1) of T_SM_SETTINGS;
    //signal Reg             : T_ARR_SM_SETTINGS;
    reg [2:0] 	   main_state;
    reg [NUM_STAGES + 1:1] start;
    wire [NUM_STAGES + 1:1] idle;
    wire [NUM_STAGES:1]     start_PB;
    wire [NUM_STAGES:1]     ready_PB;
    wire [1:0] 		    fsm[NUM_STAGES:1];
    reg 		    start1_d;  

    // @todo: manually fix
    //signal RSM             : T_SM_SETTINGS;
    
    reg 		    out_mux_ctrl_s;
    reg 		    out_mux_ctrl_s2;  

    
    // @todo: fix, need to explicitly list record
    //fdct_sm_settings <= Reg(1);
    //zig_sm_settings  <= Reg(2);
    //qua_sm_settings  <= Reg(3);
    //rle_sm_settings  <= Reg(4);
    //huf_sm_settings  <= Reg(5);
    //bs_sm_settings   <= Reg(6);
    
    assign fdct_start = start_PB[1];
    assign ready_PB[1] = fdct_ready;
    assign zig_start = start_PB[2];
    assign ready_PB[2] = zig_ready;
    assign qua_start = start_PB[3];
    assign ready_PB[3] = qua_ready;
    assign rle_start = start_PB[4];
    assign ready_PB[4] = rle_ready;
    assign huf_start = start_PB[5];
    assign ready_PB[5] = huf_ready;
    assign bs_start = start_PB[6];
    assign ready_PB[6] = bs_ready;
    
    //---------------------------------------------------------------------------
    // CTRLSM 1..NUM_STAGES
    //---------------------------------------------------------------------------
    genvar gi;
    generate
	for(gi=0; gi < NUM_STAGES; gi=gi+1) begin : G_CTRL_SM
	    SingleSM
	       U_S_CTRL_SM
	       (.CLK          (CLK          ),
		.RST          (RST          ),
		//-- from/to SM(m)   
		.start_i      (start(gi)     ),      
		.idle_o       (idle(gi)      ),
		//-- from/to SM(m+1) 
		.idle_i       (idle[gi+1]    ),      
		.start_o      (start[gi+1]   ),
		//-- from/to processing block
		.pb_rdy_i     (ready_PB[gi]  ),     
		.pb_start_o   (start_PB[gi]  ),
		//-- state out
		.fsm_o        (fsm[gi]       )
		);	    
	end
    endgenerate
    
    // @todo: manually convert
    //G_S_CTRL_SM : for i in 1 to NUM_STAGES generate
    //
    //  -- CTRLSM 1..NUM_STAGES
    //  U_S_CTRL_SM : entity work.SingleSM
    //  port map
    //  (
    //      CLK          => CLK,
    //      RST          => RST,      
    //      -- from/to SM(m)   
    //      start_i      => start(i),      
    //      idle_o       => idle(i),
    //      -- from/to SM(m+1) 
    //      idle_i       => idle(i+1),      
    //      start_o      => start(i+1),
    //      -- from/to processing block
    //      pb_rdy_i     => ready_PB(i),     
    //      pb_start_o   => start_PB(i),
    //      -- state out
    //      fsm_o        => fsm(i)
    //  );
    //end generate G_S_CTRL_SM;
    
    assign idle[NUM_STAGES + 1] =  ~outif_almost_full;
    //-----------------------------------------------------------------
    // Regs
    //-----------------------------------------------------------------
    genvar 		    i;
    generate for (i=1; i <= NUM_STAGES; i = i + 1) begin: G_REG_SM
	always @(posedge CLK or posedge RST) begin
	    if(RST == 1'b 1) begin
		Reg[i] <= C_SM_SETTINGS;
	    end else begin
		if(start[i] == 1'b 1) begin
		    // @todo: manually convert
		    //if i = 1 then
		    //  -- @todo: manually convert
		    //  --Reg(i).x_cnt   <= RSM.x_cnt;
		    //  --Reg(i).y_cnt   <= RSM.y_cnt;
		    //  --Reg(i).cmp_idx <= RSM.cmp_idx;
		    //else
		    //  Reg(i) <= Reg(i-1);
		    //end if;                  
		end
	    end
	end	
    end
    endgenerate
    
    //-----------------------------------------------------------------
    // Main_SM
    //-----------------------------------------------------------------
    always @(posedge CLK or posedge RST) begin
	if(RST == 1'b 1) begin
	    main_state <= IDLES;
	    start[1] <= 1'b 0;
	    start1_d <= 1'b 0;
	    jpeg_ready <= 1'b 0;
	    RSM.x_cnt <= {1{1'b0}};
	    RSM.y_cnt <= {1{1'b0}};
	    jpeg_busy <= 1'b 0;
	    RSM.cmp_idx <= {1{1'b0}};
	    out_mux_ctrl_s <= 1'b 0;
	    out_mux_ctrl_s2 <= 1'b 0;
	    jfif_eoi <= 1'b 0;
	    out_mux_ctrl <= 1'b 0;
	    jfif_start <= 1'b 0;
	end else begin
	    start[1] <= 1'b 0;
	    start1_d <= start[1];
	    jpeg_ready <= 1'b 0;
	    jfif_start <= 1'b 0;
	    out_mux_ctrl_s2 <= out_mux_ctrl_s;
	    out_mux_ctrl <= out_mux_ctrl_s2;
	    
	    case(main_state)	      
              //-----------------------------
	      // IDLE
	      //-----------------------------
	      IDLES : begin
		  if(sof == 1'b 1) begin
		      RSM.x_cnt <= {1{1'b0}};
		  RSM.y_cnt <= {1{1'b0}};
		  jfif_start <= 1'b 1;
		  out_mux_ctrl_s <= 1'b 0;
		  jfif_eoi <= 1'b 0;
		  main_state <= JFIF;
              end
		  //-----------------------------
		  // JFIF
		  //-----------------------------
	      end
	      JFIF : begin
		  if(jfif_ready == 1'b 1) begin
		      out_mux_ctrl_s <= 1'b 1;
		      main_state <= HORIZ;
		  end
		  //-----------------------------
		  // HORIZ
		  //-----------------------------
	      end
	      HORIZ : begin
		  if(RSM.x_cnt < ((img_size_x))) begin
		      main_state <= COMP;
		  end
		  else begin
		      RSM.x_cnt <= {1{1'b0}};
		  main_state <= VERT;
              end
		  //-----------------------------
		  // COMP
		  //-----------------------------
	      end
	      COMP : begin
		  if(idle[1] == 1'b 1 && start[1] == 1'b 0) begin
          if(RSM.cmp_idx < ((CMP_MAX))) begin
              start[1] <= 1'b 1;
          end
          else begin
              RSM.cmp_idx <= {1{1'b0}};
          RSM.x_cnt <= RSM.x_cnt + 16;
          main_state <= HORIZ;
      end
		  end
		  //-----------------------------
		  // VERT
		  //-----------------------------
	      end
	      VERT : begin
		  if(RSM.y_cnt < (((img_size_y)) - 8)) begin
		      RSM.x_cnt <= {1{1'b0}};
		  RSM.y_cnt <= RSM.y_cnt + 8;
		  main_state <= HORIZ;
        end
		  else begin
		      // @todo: manually convert
		      //if idle(NUM_STAGES+1 downto 1) = (NUM_STAGES+1 downto 1 => '1') then
		      //  main_state     <= EOI;
		      //  jfif_eoi       <= '1';
		      //  out_mux_ctrl_s <= '0';
		      //  jfif_start     <= '1';
		      //end if;
		  end
		  //-----------------------------
		  // VERT
		  //-----------------------------
	      end
	      EOI : begin
		  if(jfif_ready == 1'b 1) begin
		      jpeg_ready <= 1'b 1;
		      main_state <= IDLES;
		  end
		  //-----------------------------
		  // others
		  //-----------------------------
	      end
	      default : begin
		  main_state <= IDLES;
	      end
	    endcase
	    if(start1_d == 1'b 1) begin
		RSM.cmp_idx <= RSM.cmp_idx + 1;
	    end
	    if(main_state == IDLES) begin
		jpeg_busy <= 1'b 0;
	    end
	    else begin
		jpeg_busy <= 1'b 1;
	    end
	end
    end
    
endmodule
