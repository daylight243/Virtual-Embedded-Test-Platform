`include "protection_states.vh"

module protection_outputs(
    input wire [2:0] state_code,

    output reg alarm,
    output reg shutdown 
);

    always @(*) begin 

        alarm = 1'b0;
        shutdown = 1'b0;

        if (state_code == `STATE_FAULT) begin
            alarm = 1'b1;
            shutdown = 1'b1;
        end

    end

endmodule 