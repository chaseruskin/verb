// Module: alu
//
// The Arithmetic Logic Unit is the Function Unit responsible for basic 
// integer operations.
//
// See: docs/modules/alu/README.md

module alu
    import sys_defs::*;
#(
    // No parameters
) (
    input DATA     opa,
    input DATA     opb,
    input ALU_FUNC alu_func,

    output DATA    result
);

    always_comb begin
        case (alu_func)
            ALU_ADD:  result = opa + opb;
            ALU_SUB:  result = opa - opb;
            ALU_AND:  result = opa & opb;
            ALU_SLT:  result = signed'(opa) < signed'(opb);
            ALU_SLTU: result = opa < opb;
            ALU_OR:   result = opa | opb;
            ALU_XOR:  result = opa ^ opb;
            ALU_SRL:  result = opa >> opb[4:0];
            ALU_SLL:  result = opa << opb[4:0];
            ALU_SRA:  result = signed'(opa) >>> opb[4:0]; // arithmetic from logical shift
            // here to prevent latches:
            default:  result = 32'hdeadbeef;
        endcase
    end

endmodule // alu
