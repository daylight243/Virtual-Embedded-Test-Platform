`include "protection_states.vh"
module protection_next_state(
    input wire [2:0] current_state,
    input wire start,
    input wire confirmed_fault,
    output reg [2:0] next_state
);

    always@(*)begin

        next_state = current_state;
        
        case(current_state)
            
            `STATE_IDLE: begin
                if(start)
                 next_state = `STATE_STARTUP;
            end

            `STATE_STARTUP: begin 
                next_state = `STATE_RUNNING;
            end

            `STATE_RUNNING: begin
                if (confirmed_fault)
                    next_state = `STATE_FAULT;
            end

            `STATE_FAULT: begin
                next_state = `STATE_FAULT;
            end

            `STATE_RECOVERY: begin
                next_state = `STATE_IDLE;
            end

            default: begin
                next_state = `STATE_IDLE;
            end
        endcase
    end
endmodule

