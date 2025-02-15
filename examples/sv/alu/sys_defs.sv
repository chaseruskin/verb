package sys_defs; 

    ///////////////////////////////
    // --- CPU Configuration --- //
    ///////////////////////////////

    localparam real CLOCK_PERIOD = 16.0;

    // The superscalar-ness of the CPU
    localparam int N = 2;
    // The number of bits needed to represent the number of physical registers
    localparam int PHYS_REG_WIDTH = 6;
    // Number of bits of history to keep for indexing into PHT
    localparam int GHR_WIDTH = 4;
    // GSHARE (0), 1/2-speculative GSHARE (1), Bimodal (2), ANT (3), AT (4)
    localparam int BRANCH_PREDICTOR = 0;
    // Number of entries in the RAS (set to 0 to disable)
    localparam int RAS_DEPTH = 16;
    // How wide the BTB index is (size is 2**BTB_INDEX_WIDTH)
    localparam int BTB_INDEX_WIDTH = 5;
    // Instruction buffer (prefetching)
    localparam int INSN_BUFFER_SIZE = 16;
    // Data cache
    localparam int DCACHE_NUM_MSHRS = 8;
    localparam int DCACHE_ASSOC = 4;
    // Instruction cache
    localparam int ICACHE_NUM_MSHRS = 8;
    localparam int ICACHE_ASSOC = 1;
    // Reorder buffer
    localparam int ROB_ROWS = 12;
    // Reservation station
    localparam int RS_DEPTH = 16;
    // Function units
    localparam int NUM_FU_ALU = 2;
    localparam int NUM_FU_MULT = 1;
    localparam int NUM_FU_LS = 2;
    localparam int NUM_FU_CBU = 1;
    localparam int MULT_STAGES = 8;
    // Store queue
    localparam int SQ_DEPTH = 8;
    // Load-Store unit
    localparam int LS_ASYNC_BUFFER_SIZE = 8;


    ///////////////////////////////
    // ---- Basic Types -------- //
    ///////////////////////////////

    // word and register sizes
    typedef logic [31:0] ADDR;
    typedef logic [31:0] DATA;
    typedef logic [4:0]  REG_IDX;

    // MEMORY types (for mem.sv)
    typedef logic [3:0] MEM_TAG;


    ///////////////////////////////
    // ---- Basic Constants ---- //
    ///////////////////////////////

    // useful boolean single-bit definitions
    localparam int FALSE = 1'h0;
    localparam int TRUE = 1'h1;

    // the zero register
    // In RISC-V, any read of this register returns zero and any writes are thrown away
    /* svlint off localparam_type_twostate */
    localparam logic[4:0] ZERO_REG = 5'd0;

    // Basic NOP instruction. Allows pipline registers to clearly be reset with
    // an instruction that does nothing instead of Zero which is really an ADDI x0, x0, 0
    /* svlint off localparam_type_twostate */
    localparam logic[31:0] NOP = 32'h00000013;

    //////////////////////////////////
    // ---- Memory Definitions ---- //
    //////////////////////////////////

    // Cache mode removes the byte-level interface from memory, so it always returns
    // a double word. The original processor won't work with this defined. Your new
    // processor will have to account for this effect on mem.
    // Notably, you can no longer write data without first reading.
    // TODO: uncomment this line once you've implemented your cache
    `define CACHE_MODE

    // you are not allowed to change this definition for your final processor
    // the project 3 processor has a massive boost in performance just from having no mem latency
    // see if you can beat it's CPI in project 4 even with a 100ns latency!
    // localparam int MEM_LATENCY_IN_CYCLES = 0;
    localparam int MEM_LATENCY_IN_CYCLES = 100.0/CLOCK_PERIOD+0.49999;
    // the 0.49999 is to force ceiling(100/period). The default behavior for
    // float to integer conversion is rounding to nearest

    // memory tags represent a unique id for outstanding mem transactions
    // 0 is a sentinel value and is not a valid tag
    localparam int NUM_MEM_TAGS = 15;

    // D-cache definitions
    localparam int DCACHE_LINES = 32;
    localparam int DCACHE_LINES_BITS = $clog2(DCACHE_LINES);

    // I-cache definitions
    localparam int ICACHE_LINES = 32;
    localparam int ICACHE_LINE_BITS = $clog2(ICACHE_LINES);

    localparam int MEM_SIZE_IN_BYTES = 64*1024;
    localparam int MEM_64BIT_LINES = MEM_SIZE_IN_BYTES/8;

    typedef enum logic[1:0] {
        FU_ALU,     // 0
        FU_MULT,    // 1
        FU_LS,      // 2
        FU_CBU      // 3  
    } FUNC_UNIT;

    // A memory or cache block
    typedef union packed {
        logic [7:0][7:0]  byte_level;
        logic [3:0][15:0] half_level;
        logic [1:0][31:0] word_level;
        logic      [63:0] dbbl_level;
    } MEM_BLOCK;

    typedef enum logic [1:0] {
        BYTE   = 2'h0,
        HALF   = 2'h1,
        WORD   = 2'h2,
        DOUBLE = 2'h3
    } MEM_SIZE;

    // Memory bus commands
    typedef enum logic [1:0] {
        MEM_NONE   = 2'h0,
        MEM_LOAD   = 2'h1,
        MEM_STORE  = 2'h2
    } MEM_COMMAND;

    // I-cache tag struct
    typedef struct packed {
        logic [12-ICACHE_LINE_BITS:0] tags;
        logic                          valid;
    } ICACHE_TAG;

    ///////////////////////////////
    // ---- Exception Codes ---- //
    ///////////////////////////////

    /**
    * Exception codes for when something goes wrong in the processor.
    * Note that we use HALTED_ON_WFI to signify the end of computation.
    * It's original meaning is to 'Wait For an Interrupt', but we generally
    * ignore interrupts in 470
    *
    * This mostly follows the RISC-V Privileged spec
    * except a few add-ons for our infrastructure
    * The majority of them won't be used, but it's good to know what they are
    */

    typedef enum logic [3:0] {
        INST_ADDR_MISALIGN  = 4'h0,
        INST_ACCESS_FAULT   = 4'h1,
        ILLEGAL_INST        = 4'h2,
        BREAKPOINT          = 4'h3,
        LOAD_ADDR_MISALIGN  = 4'h4,
        LOAD_ACCESS_FAULT   = 4'h5,
        STORE_ADDR_MISALIGN = 4'h6,
        STORE_ACCESS_FAULT  = 4'h7,
        ECALL_U_MODE        = 4'h8,
        ECALL_S_MODE        = 4'h9,
        NO_ERROR            = 4'ha, // a reserved code that we use to signal no errors
        ECALL_M_MODE        = 4'hb,
        INST_PAGE_FAULT     = 4'hc,
        LOAD_PAGE_FAULT     = 4'hd,
        HALTED_ON_WFI       = 4'he, // 'Wait For Interrupt'. In 470, signifies the end of computation
        STORE_PAGE_FAULT    = 4'hf
    } EXCEPTION_CODE;

    ///////////////////////////////////
    // ---- Instruction Typedef ---- //
    ///////////////////////////////////

    // from the RISC-V ISA spec
    typedef union packed {
        logic [31:0] inst;
        struct packed {
            logic [6:0] funct7;
            logic [4:0] rs2; // source register 2
            logic [4:0] rs1; // source register 1
            logic [2:0] funct3;
            logic [4:0] rd; // destination register
            logic [6:0] opcode;
        } r; // register-to-register instructions
        struct packed {
            logic [11:0] imm; // immediate value for calculating address
            logic [4:0]  rs1; // source register 1 (used as address base)
            logic [2:0]  funct3;
            logic [4:0]  rd;  // destination register
            logic [6:0]  opcode;
        } i; // immediate or load instructions
        struct packed {
            logic [6:0] off; // offset[11:5] for calculating address
            logic [4:0] rs2; // source register 2
            logic [4:0] rs1; // source register 1 (used as address base)
            logic [2:0] funct3;
            logic [4:0] set; // offset[4:0] for calculating address
            logic [6:0] opcode;
        } s; // store instructions
        struct packed {
            logic       of;  // offset[12]
            logic [5:0] s;   // offset[10:5]
            logic [4:0] rs2; // source register 2
            logic [4:0] rs1; // source register 1
            logic [2:0] funct3;
            logic [3:0] et;  // offset[4:1]
            logic       f;   // offset[11]
            logic [6:0] opcode;
        } b; // branch instructions
        struct packed {
            logic [19:0] imm; // immediate value
            logic [4:0]  rd; // destination register
            logic [6:0]  opcode;
        } u; // upper-immediate instructions
        struct packed {
            logic       of; // offset[20]
            logic [9:0] et; // offset[10:1]
            logic       s;  // offset[11]
            logic [7:0] f;  // offset[19:12]
            logic [4:0] rd; // destination register
            logic [6:0] opcode;
        } j;  // jump instructions

    // extensions for other instruction types
    `ifdef ATOMIC_EXT
        struct packed {
            logic [4:0] funct5;
            logic       aq;
            logic       rl;
            logic [4:0] rs2;
            logic [4:0] rs1;
            logic [2:0] funct3;
            logic [4:0] rd;
            logic [6:0] opcode;
        } a; // atomic instructions
    `endif
    `ifdef SYSTEM_EXT
        struct packed {
            logic [11:0] csr;
            logic [4:0]  rs1;
            logic [2:0]  funct3;
            logic [4:0]  rd;
            logic [6:0]  opcode;
        } sys; // system call instructions
    `endif

    } INST; // instruction typedef, this should cover all types of instructions

    ////////////////////////////////////////
    // ---- Datapath Control Signals ---- //
    ////////////////////////////////////////

    // ALU opA input mux selects
    typedef enum logic [1:0] {
        OPA_IS_RS1  = 2'h0,
        OPA_IS_NPC  = 2'h1,
        OPA_IS_PC   = 2'h2,
        OPA_IS_ZERO = 2'h3
    } ALU_OPA_SELECT;

    // ALU opB input mux selects
    typedef enum logic [3:0] {
        OPB_IS_RS2    = 4'h0,
        OPB_IS_I_IMM  = 4'h1,
        OPB_IS_S_IMM  = 4'h2,
        OPB_IS_B_IMM  = 4'h3,
        OPB_IS_U_IMM  = 4'h4,
        OPB_IS_J_IMM  = 4'h5
    } ALU_OPB_SELECT;

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

    // MULT funct3 code
    // we don't include division or rem options
    typedef enum logic [2:0] {
        M_MUL,
        M_MULH,
        M_MULHSU,
        M_MULHU
    } MULT_FUNC;

    ////////////////////////////////
    // ---- Datapath Packets ---- //
    ////////////////////////////////

    // Decode packet
    // Control signals related to each instruction that must propogate through
    // execution with that instruction
    typedef struct packed {
        INST inst;
        ADDR PC;
        ADDR prediction_target;    // A branch's prediction pc destination
        ALU_OPA_SELECT opa_select; // ALU opa mux select (ALU_OPA_xxx *)
        ALU_OPB_SELECT opb_select; // ALU opb mux select (ALU_OPB_xxx *)
        logic     has_dest;        // destination (writeback) register index
        ALU_FUNC  alu_func;        // ALU function select (ALU_xxx *)
        FUNC_UNIT fu;              // Function unit
        logic     mult;            // Is inst a multiply instruction?
        logic     rd_mem;          // Does inst read memory?
        logic     wr_mem;          // Does inst write memory?
        MEM_SIZE  mem_size;        // How many bytes do you take from the data?
        logic     rd_signedness;   // Is a read from memory a signed or unsigned read? (sign extend, if signed)
        logic     cond_branch;     // Is inst a conditional branch?
        logic     uncond_branch;   // Is inst an unconditional branch?
        logic     cond_prediction; // Prediction for conditional branch
        logic     halt;            // Is this a halt?
        logic     illegal;         // Is this instruction illegal?
        logic     csr_op;          // Is this a CSR operation? (we only used this as a cheap way to get return code)
        logic     valid;
    } DECODE_PACKET;

    // Retire packet
    // Controls signals that must be kept in ROB while instruction awaits retirement
    typedef struct packed {
        ADDR        pc;
        // logical destination register
        REG_IDX     rd; 
        logic       halt;
        logic       illegal;
        logic       is_uncond_branch;
        logic       is_cond_branch;
        // does this branch have writeback?
        logic       has_dest;
    } RETIRE_PACKET;

    // FETCH_DISPATCH_PACKET
    typedef struct packed {
        logic occupied;
        logic bp_eaten;
        logic insn_valid;
        ADDR branch_target; // only valid if is_branch
        ADDR insn_addr;
        INST  insn;
        logic branch_pred;
        logic cond_branch;
        logic uncond_branch;
        logic is_store;
        logic is_load;
        logic illegal;
        logic is_call;
        logic is_return;
    } FETCH_DISPATCH_PACKET;

endpackage
