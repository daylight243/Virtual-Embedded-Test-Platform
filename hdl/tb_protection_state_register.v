`timescale 1ns/1ps

`include "protection_states.vh"

module tb_protection_state_register;
    reg clk;
    reg reset;
    reg [2:0] next_state;

    wire [2:0] state_code;

    protection_state_register dut (
        .clk(clk),
        .reset(reset),
        .next_state(next_state),
        .state_code(state_code)
    );
    
    initial begin 
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        $dumpfile("build/protection_state_register.vcd");
        $dumpvars(0, tb_protection_state_register);

        reset = 1;
        next_state = `STATE_IDLE;

        $display("========================================"); 
        $display("Virtual FPGA - State Register Test"); 
        $display("========================================"); 
        $display("");

        //Allow a rising edge while reset is active
        #6;


        if (state_code == `STATE_IDLE)
            $display("PASS: Reset places controller in IDLE");
        else
            $display("FAIL: Reset did not produce IDLE");

        reset = 0;

        //Request STARTUP
        next_state = `STATE_STARTUP;
       
        #10;

        if (state_code == `STATE_STARTUP)
            $display("PASS: Loaded STARTUP");
        else 
            $display("FAIL: Could not load STARTUP");
 
        
        //Request RUNNING
        next_state = `STATE_RUNNING;
       
        #10;

        if (state_code == `STATE_RUNNING)
            $display("PASS: Loaded RUNNING");
        else 
            $display("FAIL: Could not load RUNNING");

        
        
        //Request FAULT
        next_state = `STATE_FAULT;
       
        #10;

        if (state_code == `STATE_FAULT)
            $display("PASS: Loaded FAULT");
        else 
            $display("FAIL: Could not load FAULT");

        
        //Request RECOVERY
        next_state = `STATE_RECOVERY;
       
        #10;

        if (state_code == `STATE_RECOVERY)
            $display("PASS: Loaded RECOVERY");
        else 
            $display("FAIL: Could not load RECOVERY");

        
        //Reset again
        reset = 1;
       
        #10;

        if (state_code == `STATE_IDLE)
            $display("PASS: Reset returned controller to IDLE");
        else 
            $display("FAIL: Reset did not return to IDLE");
        
        $display(""); 
        $display("State register test complete."); 
        $display("========================================");
        
        $finish;

    end

endmodule