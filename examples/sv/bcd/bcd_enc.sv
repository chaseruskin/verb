module bcd_enc #(
    parameter int LEN = 4,
    parameter int DIGITS = 2
) (
    input logic rst,
    input logic clk,
    input logic go,
    input logic[LEN-1:0] bin,
    output logic[(4*DIGITS)-1:0] bcd,
    output logic done,
    output logic ovfl
);

    typedef enum {S_LOAD, S_SHIFT, S_ADD, S_COMPLETE, S_WAIT} state;

    logic[$bits(bcd)+$bits(bin)-1:0] dabble_r, dabble_d;

    logic ovfl_r, ovfl_d;
    state state_r, state_d;

    localparam int CTR_LEN = $clog2(LEN);

    logic[CTR_LEN-1:0] ctr_r, ctr_d;

    // registers with positive async reset
    always_ff @(posedge rst, posedge clk) begin
        if(rst == 1'b1) begin
            ovfl_r <= '0;
            dabble_r <= '0;
            ctr_r <= '0;
            state_r <= S_LOAD;
        end else begin
            state_r <= state_d;
            ctr_r <= ctr_d;
            ovfl_r <= ovfl_d;
            dabble_r <= dabble_d;
        end
    end

    // simple pass through
    assign ovfl = ovfl_r;

    // determine next state and output signals
    always_comb begin
        logic[3:0] bcd_digit;

        state_d = state_r;
        ctr_d = ctr_r;
        ovfl_d = ovfl_r;
        dabble_d = dabble_r;
        done = '0;

        bcd = dabble_r[LEN +: $bits(bcd)];

        case(state_r)
            S_LOAD: begin
                dabble_d = '0;
                dabble_d[$bits(bin)-1:0] = bin;
                ctr_d = '0;
                ovfl_d = '0;

                if(go == 1'b1) begin
                    state_d = S_SHIFT;
                end
            end
            // perform the "double" (multiply by 2)
            S_SHIFT: begin
                dabble_d = dabble_r << 1;
                ovfl_d = ovfl_r | dabble_r[$bits(dabble_r)-1];
                ctr_d = ctr_r + 1;
                if(ctr_r == (CTR_LEN)'(LEN-1)) begin
                    state_d = S_COMPLETE;
                end else begin
                    state_d = S_ADD;
                end
            end
            // perform the "dabble" (+3 when >= 5)
            S_ADD: begin
                for(int i = DIGITS-1; i >= 0; i--) begin
                    bcd_digit = dabble_r[(4*i)+LEN +: 4];
                    if(bcd_digit >= 5) begin
                        dabble_d[(4*i)+LEN +: 4] = bcd_digit + 3;
                    end
                end
                state_d = S_SHIFT;
            end
            S_COMPLETE: begin
                done = 1'b1;
                ovfl_d = ovfl_r;
                state_d = S_WAIT;
            end
            S_WAIT: begin
                done = 1'b1;
                // uncomment this line to see stability issues
                // bcd = '0;
                state_d = S_LOAD;
            end
            default: begin
                state_d = S_LOAD;
            end
        endcase
    end

endmodule
