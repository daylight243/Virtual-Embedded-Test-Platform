`timescale 1ns/1ps
module  tb_protection_input_demo;
    reg undervoltage;
    reg overcurrent;

    wire alarm;

    protection_input_demo dut(
        .undervoltage(undervoltage),
        .overcurrent(overcurrent),
        .alarm(alarm)
    );
    
    initial begin
        
    
        $dumpfile("build/protection_input_demo.vcd");
        $dumpvars(0, tb_protection_input_demo);

        $display("========================================");
        $display("Virtual FPGA - First HDL Test"); 
        $display("========================================"); 
        $display("");

        // Test 1
        undervoltage = 0;
        overcurrent = 0;

        #10;

        $display ("Test 1: Healthy Inputs");
        if (alarm == 0)
            $display("PASS");
        else
            $display("FAIL");

        // Test 2
        undervoltage = 1;
        overcurrent = 0;

        #10;

        $display ("Test 2: Undervoltage");
        if (alarm == 1)
            $display("PASS");
        else
            $display("FAIL");

        // Test 3
        undervoltage = 0;
        overcurrent =1;

        #10;

        $display ("Test 3: Overcurrent");
        if (alarm == 1)
            $display("PASS");
        else
            $display("FAIL");

        //Test 4
        undervoltage = 1;
        overcurrent = 1;

        #10;
        
        $display ("Test 4: Both Faults");
        if (alarm == 1)
            $display("PASS");
        else
            $display("FAIL");

        $display(""); 
        $display("Simulation complete.");
        $display("========================================");
        
        $finish;
    end
   


endmodule