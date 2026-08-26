`timescale 1ns/1ps

`include "protection_states.vh"
module tb_protection_fsm;
    reg clk;
    reg reset;
    reg start;

    reg undervoltage;
    reg overvoltage;
    reg overcurrent;
    reg overtemperature;

    wire [2:0] state_code;
    wire fault_present;
    wire [2:0] fault_code;

    protection_fsm dut (
        
        .clk(clk), 
        .reset(reset), 
        .start(start), 
        
        .undervoltage(undervoltage), 
        .overvoltage(overvoltage),
        .overcurrent(overcurrent), 
        .overtemperature(overtemperature), 
        
        .state_code(state_code),
        .fault_present(fault_present),
        .fault_code(fault_code)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        $dumpfile("build/protection_fsm.vcd");
        $dumpvars(0, tb_protection_fsm);

        reset = 1;
        start = 0;

        undervoltage = 0;
        overvoltage = 0;
        overcurrent = 0;
        overtemperature = 0;

        $display("========================================"); 
        $display("Virtual FPGA - FSM Test");
        $display("========================================"); 
        $display("");

        // Initial reset. 
        #6; 
        if (state_code == `STATE_IDLE) 
           $display("PASS: Reset -> IDLE"); 
        else 
           $display("FAIL: Reset -> IDLE");

        // Release reset and verify IDLE holds.
        reset = 0; 
        #10; 
        if (state_code == `STATE_IDLE) 
            $display("PASS: IDLE holds without START"); 
        else
            $display("FAIL: IDLE did not hold"); 
            
        // Request startup. 
        start = 1; 
        #10; 
        if (state_code == `STATE_STARTUP) 
            $display("PASS: IDLE + START -> STARTUP"); 
        else 
            $display("FAIL: START transition"); 
        
        // Remove START. 
        start = 0; 
        #10; 
        if (state_code == `STATE_RUNNING) 
            $display("PASS: STARTUP -> RUNNING");
        else 
            $display("FAIL: STARTUP transition"); 

        // Try START again while already RUNNING. 
        start = 1;
        #10; 
        if (state_code == `STATE_RUNNING) 
            $display("PASS: START ignored while RUNNING"); 
        else 
            $display("FAIL: Invalid RUNNING transition"); 
        
        start = 0;
        // Test Winning fault and FSM transition
        undervoltage = 1;
        overvoltage = 1;
        overtemperature = 1;
        overcurrent = 1;

        #1;
        if (fault_code == `FAULT_OVERCURRENT)
            $display("PASS: Integrated priority selects OC");
        else
            $display("FAIL: Integrated fault priority");

        #9;
        if (state_code == `STATE_FAULT)
            $display("PASS: Prioritized fault drives FSM to FAULT");
        else
            $display("FAIL: Prioritized fault did not trigger FAULT");
        

        // Remove fault. FAULT should remain latched. 
        undervoltage = 0;
        overvoltage = 0;
        overcurrent = 0;
        overtemperature = 0;
        #10; 
        if (state_code == `STATE_FAULT) 
            $display("PASS: FAULT remains latched"); 
        else 
            $display("FAIL: FAULT did not remain latched"); 
        // Global reset returns the controller to IDLE. 
            reset = 1; 
            #10; 
        if (state_code == `STATE_IDLE) 
            $display("PASS: Reset returns FAULT -> IDLE"); 
        else 
            $display("FAIL: Reset did not return to IDLE"); 
            $display(""); 
            $display("FSM test complete."); 
            $display("========================================"); 
        
        $finish;
    end 
endmodule
    
