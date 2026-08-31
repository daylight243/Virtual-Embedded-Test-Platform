`include "fault_codes.vh"

module fault_latch(
    input wire clk,
    input wire reset,
    input wire confirmed_fault,

    input wire [2:0] active_fault_code,
    output reg [2:0] stored_fault_code
);

    always@(posedge clk) begin
        if (reset) begin
            stored_fault_code <= `FAULT_NONE;
        end
        else if (confirmed_fault && stored_fault_code == `FAULT_NONE) begin
            stored_fault_code <= active_fault_code;
        end

    end
endmodule