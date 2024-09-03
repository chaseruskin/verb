module add #(
    parameter integer WORD_SIZE = 32
) (
    input logic cin,
    input logic[WORD_SIZE-1:0] in0,
    input logic[WORD_SIZE-1:0] in1,
    output logic[WORD_SIZE-1:0] sum,
    output logic cout
);

    logic[WORD_SIZE:0] intermediate;

    assign intermediate = {1'b0, in0} + {1'b0, in1} + {WORD_SIZE'(0), cin};

    assign sum = intermediate[WORD_SIZE-1:0];
    assign cout = intermediate[WORD_SIZE];

endmodule
