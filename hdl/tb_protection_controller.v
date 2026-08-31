`timescale 1ns/1ps

`include "protection_states.vh"
`include "fault_codes.vh"

module tb_protection_controller;
    reg clk;
    reg reset;
    reg start;

    reg undervoltage;
    reg overvoltage;
    reg overcurrent;
    reg overtemperature;

    wire alarm;
    wire shutdown;

    wire [2:0] fault_code;
    wire [2:0] state_code;

    wire fault_present;
    wire confirmed_fault;
    wire [1:0] fault_count;

    integer passed_tests;
    integer failed_tests;

    protection_fsm dut (
        .clk(clk),
        .reset(reset),
        .start(start),

        .undervoltage(undervoltage),
        .overvoltage(overvoltage),
        .overcurrent(overcurrent),
        .overtemperature(overtemperature),

        .alarm(alarm),
        .shutdown(shutdown),
        .fault_code(fault_code),
        .state_code(state_code),

        .fault_present(fault_present),
        .confirmed_fault(confirmed_fault),
        .fault_count(fault_count)
    );

    // -------------------------------------------------
    // Clock
    // -------------------------------------------------

    initial begin 
        clk = 0;
        forever #5 clk = ~clk;
    end

    // -------------------------------------------------
    // Helper: clear all electrical fault inputs
    // -------------------------------------------------

    task clear_faults;
        begin
            undervoltage = 0;
            overvoltage = 0;
            overcurrent = 0;
            overtemperature = 0;
        end
    endtask

    // -------------------------------------------------
    // Helper: return controller to clean IDLE condition
    // -------------------------------------------------

    task reset_to_idle;
        begin
            @(negedge clk);

            start = 0;
            clear_faults;
            reset = 1;

            @(posedge clk);
            
            #1;

            @(negedge clk);

            reset = 0;

            @(posedge clk);

            #1;

            if (
                state_code == `STATE_IDLE &&
                fault_code == `FAULT_NONE &&
                alarm == 0 &&
                shutdown == 0
            ) begin

                $display("PASS: Controller reset to clean IDLE");
                passed_tests = passed_tests + 1;
        
            end
            else begin

                $display("FAIL: Controller did not reset to clean IDLE");

                failed_tests = failed_tests + 1;

            end

        end

    endtask
    
    // -------------------------------------------------
    // Helper: IDLE -> STARTUP -> RUNNING
    // -------------------------------------------------

    task start_controller;
        begin
            @(negedge clk);
            
            start = 1;

            @(posedge clk);

            #1;

            if (state_code == `STATE_STARTUP)
                begin
                     if (state_code == `STATE_STARTUP) begin

                        $display("PASS: IDLE + START -> STARTUP");

                        passed_tests = passed_tests + 1;

                    end
                    else begin

                        $display("FAIL: STARTUP transition");

                        failed_tests = failed_tests + 1;

                    end
                end
            @(negedge clk);

            start = 0;

            @(posedge clk);
            #1;

            if (state_code == `STATE_RUNNING) begin

                $display("PASS: STARTUP -> RUNNING");

                passed_tests = passed_tests + 1;

            end
            else begin

                $display("FAIL: RUNNING transition");

                failed_tests = failed_tests + 1;

            end

        end

    endtask
    
    // -------------------------------------------------
    // Main verification campaign
    // -------------------------------------------------

    initial begin
        $dumpfile("build/protection_controller.vcd");
        $dumpvars(0, tb_protection_controller);

        passed_tests = 0;
        failed_tests = 0;

        reset = 1;
        start = 0;

        undervoltage = 0;
        overvoltage = 0;
        overcurrent = 0;
        overtemperature = 0;


        $display("");
        $display("========================================");
        $display(" Virtual FPGA Comprehensive Testbench");
        $display("========================================");
        $display("");


        // =============================================
        // TEST GROUP 1
        // Reset and startup
        // =============================================

        @(posedge clk);
        #1;

        if (state_code == `STATE_IDLE) begin
            $display("PASS: Initial RESET -> IDLE");
            passed_tests = passed_tests + 1;
        end

        else begin

            $display("FAIL: Initial RESET -> IDLE");
            failed_tests = failed_tests + 1;

        end

        @(negedge clk);
        reset = 0;

        start_controller;

        // =============================================
        // TEST GROUP 2
        // Normal RUNNING
        // =============================================

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_RUNNING &&
            alarm == 0 &&
            shutdown == 0 &&
            fault_code == `FAULT_NONE
        ) begin

            $display("PASS: Normal RUNNING operation");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Normal RUNNING operation");
            failed_tests = failed_tests + 1;

        end

        // =============================================
        // TEST GROUP 3
        // Invalid START while RUNNING
        // =============================================

        
        @(negedge clk);
        start = 1;

        @(posedge clk);
        #1;

        if (state_code == `STATE_RUNNING) begin

            $display("PASS: START ignored while RUNNING");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Invalid START changed RUNNING state");
            failed_tests = failed_tests + 1;

        end

        @(negedge clk);
        start = 0;
        

        // =============================================
        // TEST GROUP 4
        // Brief transient rejection
        // =============================================

        overcurrent = 1;

        @(posedge clk);
        #1;

        if (
            fault_count == 1 &&
            confirmed_fault == 0 &&
            state_code == `STATE_RUNNING
        ) begin

            $display("PASS: 1-cycle fault not confirmed");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: 1-cycle transient handling");
            failed_tests = failed_tests + 1;

        end


        @(negedge clk);
        overcurrent = 0;

        @(posedge clk);
        #1;

        if (
            fault_count == 0 &&
            confirmed_fault == 0 &&
            state_code == `STATE_RUNNING &&
            shutdown == 0
        ) begin

            $display("PASS: Brief transient rejected");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Brief transient caused protection event");
            failed_tests = failed_tests + 1;

        end

        // =============================================
        // TEST GROUP 5
        // UNDERVOLTAGE
        // =============================================
         undervoltage = 1;

        @(posedge clk);
        #1;

        @(posedge clk);
        #1;

        if (
            fault_count == 2 &&
            confirmed_fault == 0
        ) begin

            $display("PASS: UV remains unconfirmed before threshold");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: UV persistence before threshold");
            failed_tests = failed_tests + 1;

        end


        @(posedge clk);
        #1;

        if (
            fault_count == 3 &&
            confirmed_fault == 1
        ) begin

            $display("PASS: Sustained UV becomes confirmed");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: UV confirmation threshold");
            failed_tests = failed_tests + 1;

        end


        @(posedge clk);
        #1;

        if (
            state_code == `STATE_FAULT &&
            fault_code == `FAULT_UNDERVOLTAGE &&
            alarm == 1 &&
            shutdown == 1
        ) begin

            $display("PASS: Undervoltage protection");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Undervoltage protection");
            failed_tests = failed_tests + 1;

        end


        // =============================================
        // TEST GROUP 6
        // Explicit recovery test
        // =============================================

        @(negedge clk);

        undervoltage = 0;
        reset = 1;

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_RECOVERY &&
            fault_code == `FAULT_NONE &&
            alarm == 0 &&
            shutdown == 0
        ) begin

            $display("PASS: FAULT + RESET -> RECOVERY");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Recovery entry");
            failed_tests = failed_tests + 1;

        end


        @(negedge clk);
        reset = 0;

        @(posedge clk);
        #1;

        if (state_code == `STATE_IDLE) begin

            $display("PASS: RECOVERY -> IDLE");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Recovery exit");
            failed_tests = failed_tests + 1;

        end


        // =============================================
        // TEST GROUP 7
        // OVERVOLTAGE
        // =============================================

        start_controller;

        @(negedge clk);
        overvoltage = 1;

        repeat (3) begin
            @(posedge clk);
            #1;
        end

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_FAULT &&
            fault_code == `FAULT_OVERVOLTAGE &&
            alarm == 1 &&
            shutdown == 1
        ) begin

            $display("PASS: Overvoltage protection");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Overvoltage protection");
            failed_tests = failed_tests + 1;

        end

        reset_to_idle;


        // =============================================
        // TEST GROUP 8
        // OVERCURRENT
        // =============================================

        start_controller;

        @(negedge clk);
        overcurrent = 1;

        repeat (3) begin
            @(posedge clk);
            #1;
        end

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_FAULT &&
            fault_code == `FAULT_OVERCURRENT &&
            alarm == 1 &&
            shutdown == 1
        ) begin

            $display("PASS: Overcurrent protection");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Overcurrent protection");
            failed_tests = failed_tests + 1;

        end

        reset_to_idle;


        // =============================================
        // TEST GROUP 9
        // OVERTEMPERATURE
        // =============================================

        start_controller;

        @(negedge clk);
        overtemperature = 1;

        repeat (3) begin
            @(posedge clk);
            #1;
        end

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_FAULT &&
            fault_code == `FAULT_OVERTEMPERATURE &&
            alarm == 1 &&
            shutdown == 1
        ) begin

            $display("PASS: Overtemperature protection");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Overtemperature protection");
            failed_tests = failed_tests + 1;

        end

        reset_to_idle;


        // =============================================
        // TEST GROUP 10
        // SIMULTANEOUS FAULTS
        // =============================================

        start_controller;

        @(negedge clk);

        undervoltage = 1;
        overvoltage = 1;
        overcurrent = 1;
        overtemperature = 1;

        #1;

        if (
            fault_present == 1 &&
            dut.active_fault_code == `FAULT_OVERCURRENT
        ) begin

            $display("PASS: OC wins simultaneous-fault priority");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Simultaneous-fault priority");
            failed_tests = failed_tests + 1;

        end


        repeat (3) begin
            @(posedge clk);
            #1;
        end

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_FAULT &&
            fault_code == `FAULT_OVERCURRENT
        ) begin

            $display("PASS: Priority fault stored after confirmation");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Stored simultaneous-fault cause");
            failed_tests = failed_tests + 1;

        end


        // =============================================
        // TEST GROUP 11
        // Stored fault retention
        // =============================================

        @(negedge clk);
        clear_faults;

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_FAULT &&
            fault_code == `FAULT_OVERCURRENT
        ) begin

            $display("PASS: Stored fault retained after inputs clear");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Stored fault retention");
            failed_tests = failed_tests + 1;

        end


        // =============================================
        // TEST GROUP 12
        // Final reset + recovery
        // =============================================

        @(negedge clk);
        reset = 1;

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_RECOVERY &&
            fault_code == `FAULT_NONE &&
            alarm == 0 &&
            shutdown == 0
        ) begin

            $display("PASS: Final recovery entry");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Final recovery entry");
            failed_tests = failed_tests + 1;

        end


        @(negedge clk);
        reset = 0;

        @(posedge clk);
        #1;

        if (
            state_code == `STATE_IDLE &&
            fault_code == `FAULT_NONE
        ) begin

            $display("PASS: Final recovery returns to IDLE");
            passed_tests = passed_tests + 1;

        end
        else begin

            $display("FAIL: Final recovery return");
            failed_tests = failed_tests + 1;

        end


        // =============================================
        // FINAL SUMMARY
        // =============================================

        $display("");
        $display("========================================");
        $display(" FPGA VERIFICATION SUMMARY");
        $display("========================================");
        $display("Passed tests: %0d", passed_tests);
        $display("Failed tests: %0d", failed_tests);
        $display("");


        if (failed_tests == 0)
            $display("MISSION 3 HDL RESULT: PASS");
        else
            $display("MISSION 3 HDL RESULT: FAIL");


        $display("========================================");
        $display("");

        $finish;

    end

endmodule



