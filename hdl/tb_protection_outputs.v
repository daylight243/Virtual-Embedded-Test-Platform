`timescale 1ns/1ps
`include "protection_states.vh"

module tb_protection_outputs;
    reg [2:0] state_code;
    
    wire alarm;
    wire shutdown;

    protection_outputs dut (
        .state_code(state_code),
        .alarm(alarm),
        .shutdown(shutdown)
    );

    initial begin 
        $display("========================================");
        $display("Virtual FPGA - Protection Output Test");
        $display("========================================");
        $display("");
 
    state_code = `STATE_IDLE;
    #1;
    if(alarm == 0 && shutdown == 0)
        $display ("PASS: IDLE outputs safe");
    else 
        $display ("FAIL: IDLE outputs");

    state_code = `STATE_STARTUP;
        #1;

        if (alarm == 0 && shutdown == 0)
            $display("PASS: STARTUP outputs safe");
        else
            $display("FAIL: STARTUP outputs");


        state_code = `STATE_RUNNING;
        #1;

        if (alarm == 0 && shutdown == 0)
            $display("PASS: RUNNING outputs safe");
        else
            $display("FAIL: RUNNING outputs");


        state_code = `STATE_FAULT;
        #1;

        if (alarm == 1 && shutdown == 1)
            $display("PASS: FAULT asserts alarm and shutdown");
        else
            $display("FAIL: FAULT outputs");


        state_code = `STATE_RECOVERY;
        #1;

        if (alarm == 0 && shutdown == 0)
            $display("PASS: RECOVERY outputs safe");
        else
            $display("FAIL: RECOVERY outputs");


        $display("");
        $display("Protection output test complete.");
        $display("========================================");

        $finish;

    end

endmodule

