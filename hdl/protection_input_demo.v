module protection_input_demo(
    input wire undervoltage,
    input wire overcurrent,
    output wire alarm
);
    assign alarm = undervoltage | overcurrent;

endmodule




