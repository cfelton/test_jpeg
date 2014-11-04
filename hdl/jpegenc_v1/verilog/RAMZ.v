

module RAMZ
#(
  parameter RAMADDR_W = 6,
  parameter RAMDATA_W = 12
)  
(
 input wire [RAMDATA_W-1:0] d,
 input wire [RAMADDR_W-1:0] waddr,
 input wire [RAMADDR_W-1:0] raddr,
 input wire 		    we,
 input wire 		    clk,
 output wire [RAMDATA_W-1:0] q
 );
    
    reg [RAMADDR_W-1:0]     read_addr;    
    reg [RAMDATA_W-1:0]     mem [0:64-1];
    
    assign q = mem[read_addr];
    
    
    always @(posedge clk) begin: RAMZ_RTL
	read_addr <= raddr;
	if (we) begin
            mem[waddr] <= d;
	end
    end
    
endmodule
