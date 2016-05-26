module tb_rledoublefifo;

reg clk;
reg reset;
reg [19:0] data_in;
reg wren;
reg buf_sel;
reg rd_req;
wire fifo_empty;
wire [19:0] data_out;

initial begin
    $from_myhdl(
        clk,
        reset,
        data_in,
        wren,
        buf_sel,
        rd_req
    );
    $to_myhdl(
        fifo_empty,
        data_out
    );
end

rledoublefifo dut(
    clk,
    reset,
    data_in,
    wren,
    buf_sel,
    rd_req,
    fifo_empty,
    data_out
);

endmodule
