`timescale 1ns/1ps

`include "protection_states.vh"

module tb_protection_states;
    
     initial begin

         $display("========================================");
         $display("Virtual FPGA - State Definition Test"); 
         $display("========================================"); 
         $display("");

         $display("IDLE    =%03b", `STATE_IDLE);
         $display("STARTUP   =%03b", `STATE_STARTUP);
         $display("RUNNING    =%03b", `STATE_RUNNING);
         $display("FAULT   =%03b", `STATE_FAULT);
         $display("RECOVERY   =%03b", `STATE_RECOVERY);
         
         $display("");

         if (`STATE_IDLE == 3'b000)
            $display("PASS: IDLE");
         else 
            $display("FAIL: IDLE");
        
         if (`STATE_STARTUP == 3'b001)
            $display("PASS: STARTUP");
         else 
            $display("FAIL: STARTUP");

         if (`STATE_RUNNING == 3'b010)
            $display("PASS: RUNNING");
         else 
            $display("FAIL: RUNNING");

         if (`STATE_FAULT == 3'b011)
            $display("PASS: FAULT");
         else 
            $display("FAIL: FAULT");
        
         if (`STATE_RECOVERY == 3'b100)
            $display("PASS: RECOVERY");
         else 
            $display("FAIL: RECOVERY");

         $display(""); 
         $display("State definition test complete.");
         $display("========================================");

         $finish;

     end

endmodule