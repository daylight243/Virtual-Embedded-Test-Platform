`include "protection_states.vh"

module protection_state_register(
    input wire  clk,
    input wire  reset,
    input wire [2:0] next_state,
    output reg [2:0] state_code
);

    always @(posedge clk) begin
        
        if (reset)
            state_code <= `STATE_IDLE;
        else
            state_code <= next_state;
    end
    
endmodule
