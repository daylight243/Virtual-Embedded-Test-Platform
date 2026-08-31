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
    output wire [2:0] fault_code,
    output wire confirmed_fault,
    output wire [1:0] fault_count,
    output wire alarm,
    output wire shutdown
);

    wire [2:0] next_state;
    wire [2:0] active_fault_code;

    fault_persistence fault_filter (
    .clk(clk),
    .reset(reset),
    .fault_present(fault_present),
    .confirmed_fault(confirmed_fault),
    .fault_count(fault_count)
    );

    fault_priority fault_selector (
        .undervoltage(undervoltage),
        .overvoltage(overvoltage),
        .overcurrent(overcurrent),
        .overtemperature(overtemperature),
        .fault_present(fault_present),
        .fault_code(active_fault_code)
    );

    fault_latch fault_register(
        .clk(clk),
        .reset(reset),
        .confirmed_fault(confirmed_fault),
        .active_fault_code(active_fault_code),
        .stored_fault_code(fault_code)
    );
    
    protection_next_state next_state_logic(
        .current_state(state_code), 
        .start(start), 
        .confirmed_fault(confirmed_fault),
        .next_state(next_state)
    );

    protection_state_register state_register( 
        .clk(clk), 
        .reset(reset), 
        .next_state(next_state), 
        .state_code(state_code)
    ); 

    protection_outputs output_logic(
        .state_code(state_code),
        .alarm(alarm),
        .shutdown(shutdown)
    );
    
endmodule
    