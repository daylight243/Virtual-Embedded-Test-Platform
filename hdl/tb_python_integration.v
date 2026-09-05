`timescale 1ns/1ps

`include "protection_states.vh"
`include "fault_codes.vh"

module tb_python_integration;

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


    integer input_file;
    integer output_file;
    integer scanned_fields;

    integer timestamp_in;
    integer reset_in;
    integer start_in;
    integer uv_in;
    integer ov_in;
    integer oc_in;
    integer ot_in;

    integer vector_count;

    reg [8*128-1:0] header_line;


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
    // Python-to-HDL integration
    // -------------------------------------------------

    initial begin

        $dumpfile("build/python_integration.vcd");
        $dumpvars(0, tb_python_integration);


        reset = 0;
        start = 0;

        undervoltage = 0;
        overvoltage = 0;
        overcurrent = 0;
        overtemperature = 0;

        vector_count = 0;


        $display("");
        $display("========================================");
        $display(" Python -> FPGA Integration Test");
        $display("========================================");
        $display("");

        input_file = $fopen("build/fpga_inputs.csv", "r");

        if (input_file == 0) begin

            $display( "ERROR: Could not open build/fpga_inputs.csv");

            $display("PYTHON -> FPGA RESULT: FAIL");

            $finish;

        end

        output_file = $fopen("build/fpga_outputs.csv", "w");

        if (output_file == 0) begin

            $display(
                "ERROR: Could not open build/fpga_outputs.csv"
            );

            $display(
                "PYTHON -> FPGA RESULT: FAIL"
            );

            $fclose(input_file);

            $finish;

        end

        $fdisplay(output_file, "timestamp,state_code,fault_code,alarm,shutdown");
        
        //Skip CSV header.
        scanned_fields = $fgets(header_line, input_file);
        
        while (!$feof(input_file)) begin

            scanned_fields = $fscanf(
                input_file,
                "%d,%d,%d,%d,%d,%d,%d\n",
                timestamp_in,
                reset_in,
                start_in,
                uv_in,
                ov_in,
                oc_in,
                ot_in
            );


            if (scanned_fields == 7) begin

                @(negedge clk);

                reset = reset_in;
                start = start_in;

                undervoltage = uv_in;
                overvoltage = ov_in;
                overcurrent = oc_in;
                overtemperature = ot_in;


                @(posedge clk);
                #1;


                vector_count = vector_count + 1;


                $display("t=%0d |  R=%0d S=%0d  UV=%0d OV=%0d OC=%0d OT=%0d  | state=%03b  fault=%03b  alarm=%0d  shutdown=%0d count=%0d  confirmed=%0d",
                    timestamp_in,
                    reset,
                    start,
                    undervoltage,
                    overvoltage,
                    overcurrent,
                    overtemperature,
                    state_code,
                    fault_code,
                    alarm,
                    shutdown,
                    fault_count,
                    confirmed_fault
                );

                $fdisplay(output_file, "%0d,%0d,%0d,%0d,%0d", timestamp_in, state_code, fault_code, alarm, shutdown);
        

            end
        
        end


        $fclose(input_file);
        $fclose(output_file);

        $display("");
        $display("Vectors processed: %0d", vector_count);
        $display("PYTHON -> FPGA RESULT: PASS");
        $display("========================================");
        $display("");


        $finish;

    end

endmodule

