module protection_fsm (
    input wire clk,
    input wire reset,
    input wire start,
    input wire undervoltage,
    input wire overvoltage,
    input wire overcurrent,
    input wire overtemperature,
    output wire [2:0] state_code,
    output wire fault_present,
    output wire [2:0] fault_code
);

    wire [2:0] next_state;

    fault_priority fault_selector (
        .undervoltage(undervoltage),
        .overvoltage(overvoltage),
        .overcurrent(overcurrent),
        .overtemperature(overtemperature),
        .fault_present(fault_present),
        .fault_code(fault_code)
    );
    
    protection_next_state next_state_logic(
        .current_state(state_code), 
        .start(start), 
        .fault_present(fault_present),
        .next_state(next_state)
    );

    protection_state_register state_register( 
        .clk(clk), 
        .reset(reset), 
        .next_state(next_state), 
        .state_code(state_code)
    ); 
    
endmodule
    