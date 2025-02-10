module ram 
#(
    parameter int ADDR_WIDTH,
    parameter int DATA_WIDTH
) (
    input logic clk,
    input logic rst,
    // Provide where to read/write data
    input logic[ADDR_WIDTH-1:0] waddr,
    input logic[ADDR_WIDTH-1:0] raddr,
    // Set this bit to issue a write
    input logic wen,
    // Provide data only when writing
    input logic[DATA_WIDTH-1:0] wdata,
    // The outgoing data fetched from the ram
    output logic[DATA_WIDTH-1:0] rdata
);

    logic[(2**ADDR_WIDTH)-1:0][DATA_WIDTH-1:0] mem_q;

    assign rdata = (waddr == raddr) ? wdata : mem_q[raddr];

    always_ff @(posedge clk, posedge rst) begin
        if (rst == 1'b1) begin
            mem_q <= '0;
        end else begin
            if (wen == 1'b1) begin
                mem_q[waddr] <= wdata;
            end
        end

    end

endmodule