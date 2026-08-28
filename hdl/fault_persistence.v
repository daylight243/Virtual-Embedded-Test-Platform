module fault_persistence(
    input wire clk,
    input wire reset,
    input wire fault_present,

    output reg confirmed_fault,
    output reg [1:0] fault_count
);
    
    parameter FAULT_PERSIST_CYCLES = 3;
    always@(posedge clk) begin

        if (reset) begin
            fault_count <= 2'd0;
            confirmed_fault <= 1'b0;
        end
        else if (!fault_present) begin
            fault_count <= 2'd0;
            confirmed_fault <= 1'b0;
        end
        else begin
            if (fault_count < FAULT_PERSIST_CYCLES)
                fault_count <= fault_count + 1'b1;
            
            if (fault_count >= FAULT_PERSIST_CYCLES -1)
                confirmed_fault <= 1'b1;
        end
    end
endmodule

