`include "fault_codes.vh"

module fault_priority(
    input wire undervoltage,
    input wire overvoltage,
    input wire overcurrent,
    input wire overtemperature,
    
    output reg fault_present,
    output reg [2:0] fault_code
);

    always@(*) begin 

        fault_present = 1'b0;
        fault_code = `FAULT_NONE;

        if (overcurrent) begin
            fault_present = 1'b1;
            fault_code = `FAULT_OVERCURRENT;
        end

        else if (overtemperature) begin
            fault_present = 1'b1;
            fault_code = `FAULT_OVERTEMPERATURE;
        end

        else if (overvoltage) begin
            fault_present = 1'b1;
            fault_code = `FAULT_OVERVOLTAGE;
        end

        else if (undervoltage) begin
            fault_present = 1'b1;
            fault_code = `FAULT_UNDERVOLTAGE;
        end

    end

endmodule