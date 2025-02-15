// The Arithmetic Logic Unit is the Function Unit responsible for basic 
// integer operations.
//
// See: docs/modules/fus/README.md

module alu
    import sys_defs::*;
#(
    parameter int PHYS_REG_WIDTH = 6
) (
    input var logic clock,
    input var logic reset,
    // Indicate we should clear any results currently being held
    input var logic clear,
    // Indicate we have valid data coming into the module
    input var logic en,
    // Registered data to perform computations
    input var DATA rs1,
    input var DATA rs2,
    // Determine which operation to perform
    input var ALU_FUNC alu_func,
    // Get acknowledgement from the backend (CDB) when it took the current result
    input var logic broadcasted,
    // Data from RS to know if the FU will write into the PRF
    input var logic[PHYS_REG_WIDTH-1:0] dest_tag_in,
    input var logic dest_tag_wr_en_in,
    
    // Provide the final result
    output DATA result,
    // Tell external modules that we have some data ready to send
    output logic next_valid,
    // Tell the frontend (RS) when if it can use this module on the next cycle
    output logic ready_next,
    // Data from the FU to the PRF to tell it to write result into register or not
    output logic[PHYS_REG_WIDTH-1:0] dest_tag_out,
    output logic dest_tag_wr_en_out
);

    DATA result_ff, result_next;

    // datapath-specific signals
    logic[PHYS_REG_WIDTH-1:0] dest_tag_ff;
    logic dest_tag_wr_en_ff;

    // control-specific signals
    logic valid_ff, valid_next;
    logic save_data;

    always_comb begin: l_compute
        case (alu_func)
            ALU_ADD:  result_next = rs1 + rs2;
            ALU_SUB:  result_next = rs1 - rs2;
            ALU_AND:  result_next = rs1 & rs2;
            ALU_SLT:  result_next = signed'(rs1) < signed'(rs2);
            ALU_SLTU: result_next = rs1 < rs2;
            ALU_OR:   result_next = rs1 | rs2;
            ALU_XOR:  result_next = rs1 ^ rs2;
            ALU_SRL:  result_next = rs1 >> rs2[4:0];
            ALU_SLL:  result_next = rs1 << rs2[4:0];
            ALU_SRA:  result_next = signed'(rs1) >>> rs2[4:0]; // arithmetic from logical shift
            // here to prevent latches:
            default:  result_next = 32'hdeadbeef;
        endcase
    end

    always_ff @(posedge clock) begin: l_store_result
        if (reset == 1'b1) begin
            result_ff <= '0;
            dest_tag_ff <= '0;
            dest_tag_wr_en_ff <= '0;
        end else begin
            /* svlint off explicit_if_else */
            if (save_data == 1'b1) begin
                // update registers only with valid data
                result_ff <= result_next;
                dest_tag_ff <= dest_tag_in;
                dest_tag_wr_en_ff <= dest_tag_wr_en_in;
            end
        end
    end

    // drive data outputs
    assign result = result_ff;

    assign dest_tag_out = dest_tag_ff;
    assign dest_tag_wr_en_out = dest_tag_wr_en_ff;

    always_comb begin: l_compute_control
        if (clear == 1'b1) begin
            valid_next = 1'b0;
        end else if (ready_next == 1'b1) begin
            valid_next = en;
        end else begin
            valid_next = valid_ff;
        end

        if (ready_next == 1'b1) begin
            save_data = en;
        end else begin
            save_data = 1'b0;
        end
    end

    always_ff @(posedge clock) begin: l_store_control
    // always_comb begin: l_store_control
        if (reset == 1'b1) begin
            valid_ff <= '0;
        end else begin
            valid_ff <= valid_next;
        end
    end

    // determine if the outputs are good
    assign next_valid = valid_next & ~reset;

    // check if we are available for the next cycle
    assign ready_next = (broadcasted | ~valid_ff) & ~clear;


endmodule