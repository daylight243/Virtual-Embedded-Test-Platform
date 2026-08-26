`timescale 1ns/1ps

`include "fault_codes.vh"
module tb_fault_priority;
    
    reg undervoltage;
    reg overvoltage;
    reg overcurrent;
    reg overtemperature;
    
    wire fault_present;
    wire [2:0] fault_code;

    fault_priority dut(
        .undervoltage(undervoltage),
        .overvoltage(overvoltage),
        .overcurrent(overcurrent),
        .overtemperature(overtemperature),
        .fault_present(fault_present),
        .fault_code(fault_code)
    );

    initial begin 
        
        $dumpfile("build/fault_priority.vcd");
        $dumpvars(0, tb_fault_priority);

        undervoltage = 0;
        overvoltage = 0;
        overcurrent = 0;
        overtemperature = 0;

        $display("========================================");
        $display("Virtual FPGA - Fault Priority Test");
        $display("========================================");
        $display("");

        //Test 1: No Fault.
        #10;
        if (fault_present == 0 && fault_code == `FAULT_NONE)
            $display("PASS: No fault");
        else
            $display("FAIL: No fault case");

        //Test 2: Undervoltage Only
        undervoltage = 1;

        #10;
        if (fault_present == 1 && fault_code == `FAULT_UNDERVOLTAGE)
            $display("PASS: Undervoltage selected");
        else
            $display("FAIL: Undervoltage");

        // Test 3: Overvoltage only.
        undervoltage = 0;
        overvoltage = 1;

        #10;

        if (fault_code == `FAULT_OVERVOLTAGE)
            $display("PASS: Overvoltage selected");
        else
            $display("FAIL: Overvoltage");


        // Test 4: Overtemperature only.
        overvoltage = 0;
        overtemperature = 1;

        #10;

        if (fault_code == `FAULT_OVERTEMPERATURE)
            $display("PASS: Overtemperature selected");
        else
            $display("FAIL: Overtemperature");

         // Test 5: Overcurrent only.
        overtemperature = 0;
        overcurrent = 1;

        #10;

        if (fault_code == `FAULT_OVERCURRENT)
            $display("PASS: Overcurrent selected");
        else
            $display("FAIL: Overcurrent");

        // Test 6: Undervoltage + Overvoltage.
        overcurrent = 0;
        undervoltage = 1;
        overvoltage = 1;

        #10;

        if (fault_code == `FAULT_OVERVOLTAGE)
            $display("PASS: OV beats UV");
        else
            $display("FAIL: OV/UV priority");

        // Test 7:
        // Overtemperature + overvoltage.
        undervoltage = 0;
        overvoltage = 1;
        overtemperature = 1;

        #10;

        if (fault_code == `FAULT_OVERTEMPERATURE)
            $display("PASS: OT beats OV");
        else
            $display("FAIL: OT/OV priority");


        // Test 8:
        // All faults simultaneously.
        undervoltage = 1;
        overvoltage = 1;
        overcurrent = 1;
        overtemperature = 1;

        #10;

        if (fault_code == `FAULT_OVERCURRENT)
            $display("PASS: OC wins all-fault test");
        else
            $display("FAIL: All-fault priority");

        
        $display("");
        $display("Fault priority test complete.");
        $display("========================================");

        $finish;
    end
endmodule



        
            

        


    