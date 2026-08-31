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

    wire confirmed_fault;
    wire [1:0] fault_count;

    wire alarm;
    wire shutdown;

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
        .fault_code(fault_code),

        .confirmed_fault(confirmed_fault),
        .fault_count(fault_count),

        .alarm(alarm),
        .shutdown(shutdown)
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

        
        // Test: Healthy Running Outputs.
        if (state_code == `STATE_RUNNING && alarm == 0 & shutdown == 0 && fault_code == `FAULT_NONE)
             $display("PASS: Healthy RUNNING outputs");
        else
             $display("FAIL: Healthy RUNNING outputs");

        // Try START again while already RUNNING. 
        start = 1;
        #10; 
        if (state_code == `STATE_RUNNING) 
            $display("PASS: START ignored while RUNNING"); 
        else 
            $display("FAIL: Invalid RUNNING transition"); 
        
        //Test Brief Fault causes no Shutdown.
        start = 0;
        overcurrent = 1;
        #10;
        overcurrent = 0;
        #10;
        if (state_code == `STATE_RUNNING && alarm == 0 && shutdown == 0 && fault_code == `FAULT_NONE)
            $display("PASS: Brief fault causes no shutdown");
        else
            $display("FAIL: Brief fault output behaviour");
        
        //Test Sustained OC TRIGGERS Protection Outputs.
        overcurrent = 1;
        #40;
        if (state_code == `STATE_FAULT && alarm == 1 && shutdown == 1 && fault_code == `FAULT_OVERCURRENT)
            $display("PASS: Sustained OC triggers protection outputs");
        else
            $display("FAIL: Sustained OC protection outputs");
        
        // Remove the fault.
        // FAULT should remain latched.
        overcurrent = 0;
        #10;

        if (state_code == `STATE_FAULT && fault_code == `FAULT_OVERCURRENT)
            $display("PASS: Fault cause remains stored");
        else
            $display("FAIL: Stored fault cause");

        // Global reset returns the controller to IDLE. 
        reset = 1; 
        #10; 
         if (state_code == `STATE_IDLE && fault_code == `FAULT_NONE && alarm == 0 && shutdown == 0)
            $display("PASS: Reset clears protection state");
        else
            $display("FAIL: Protection reset");
          
           // $display("DEBUG: count=%b confirmed=%b state=%b", fault_count, confirmed_fault, state_code); 
            $display(""); 
            $display("FSM test complete."); 
            $display("========================================"); 
        
        $finish;
    end 
endmodule
    
