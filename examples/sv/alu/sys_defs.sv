package sys_defs;

    typedef logic [31:0] DATA;

    // ALU function code
    typedef enum logic [3:0] {
        ALU_ADD     = 4'h0,
        ALU_SUB     = 4'h1,
        ALU_SLT     = 4'h2,
        ALU_SLTU    = 4'h3,
        ALU_AND     = 4'h4,
        ALU_OR      = 4'h5,
        ALU_XOR     = 4'h6,
        ALU_SLL     = 4'h7,
        ALU_SRL     = 4'h8,
        ALU_SRA     = 4'h9
    } ALU_FUNC;

endpackage
