
`timescale 1ns/1ps

module tb_mdct;

    reg clock;
    reg reset;

    reg [7:0] dcti;
    reg       idv;

    wire [11:0] dcto;
    wire 	odv;

    reg [31:0] 	icnt = 0;
    reg [31:0] 	ocnt = 0;

    initial begin
	$dumpfile("vcd/_tb_mdct.vcd");
	$dumpvars(0, tb_mdct);
    end

    initial begin
	$from_myhdl(clock, reset, dcti, idv);
	$to_myhdl(dcto, odv);
    end

    always @(posedge clock) begin
	if(idv) begin
	    icnt <= icnt + 1;
	end

	if(odv) begin
	    ocnt <= ocnt + 1;
	end
    end

    MDCT
      DUT
	(.clk    (clock),
	 .rst    (reset),
	 .dcti   (dcti),
	 .idv    (idv),
	 .dcto   (dcto),
	 .odv    (odv) 
	 );

endmodule
       
