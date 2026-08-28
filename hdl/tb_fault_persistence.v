`timescale 1ns/1ps

module tb_fault_persistence;
    reg clk;
    reg reset;
    reg fault_present;

    wire confirmed_fault;
    wire [1:0] fault_count;

    fault_persistence dut(
        .clk(clk),
        .reset(reset),
        .fault_present(fault_present),
        .confirmed_fault(confirmed_fault),
        .fault_count(fault_count)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        $dumpfile("build/fault_persistence.vcd");
        $dumpvars(0, tb_fault_persistence);

        reset =1;
        fault_present = 0;

        $display("========================================");
        $display("Virtual FPGA - Fault Persistence Test");
        $display("========================================");
        $display("");

        #6;

        reset = 0;
        //Brief fault: One cycle only.
        fault_present = 1;
        #10;

        if (fault_count == 1 && confirmed_fault == 0)
            $display("PASS: 1-cycle fault not confirmed");
        else
            $display("FAIL: 1-cycle transient");

        //Clear before persistence threshold.
        fault_present = 0;
        #10;

        if (
            fault_count == 0 &&
            confirmed_fault == 0
        )
            $display("PASS: Counter resets when fault clears");
        else
            $display("FAIL: Counter reset");

        // Sustained fault.
        fault_present = 1;

        #10;

        if (
            fault_count == 1 &&
            confirmed_fault == 0
        )
            $display("PASS: Persistent cycle 1");
        else
            $display("FAIL: Persistent cycle 1");


        #10;

        if (
            fault_count == 2 &&
            confirmed_fault == 0
        )
            $display("PASS: Persistent cycle 2");
        else
            $display("FAIL: Persistent cycle 2");

        #10;

        if (
            fault_count == 3 &&
            confirmed_fault == 1
        )
            $display("PASS: Persistent cycle 3 confirms fault");
        else
            $display("FAIL: Persistence threshold");

        reset = 1;
        #10

        reset = 0;
        fault_present = 1;
        #20

        fault_present = 0;
        #10
        if (
            fault_count == 0 &&
            confirmed_fault == 0
        )
            $display("PASS: 2-cycle fault rejected");
        else
            $display("FAIL: 2-cycle transient rejection");
        $finish;

    end

endmodule



