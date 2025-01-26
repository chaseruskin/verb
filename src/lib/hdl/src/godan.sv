package godan;

    int FD_EVENTS = start("events.log");

    /* tutils

        Provides test utility functions for testbench simulation. This involves
        reading interface signals, loading expected values, and various 
        simulation-specific tasks.
    */

    // Creates the file with the given `name` to prepare for simulation logging.
    function automatic int start(input string name);
        int fd = $fopen(name, "w");
        return fd;
    endfunction

    // Closes the file `fd` and sets `halt` to true and enters an infinite wait 
    // statement to signal that the simulation is complete.
    task complete(int fd);
        $fclose(fd);
        $finish;
    endtask

    // Asynchronous asserts `pin` and synchronously de-asserts `pin` on the
    // `cycles`'th clock edge.
    task automatic async_on_sync_off(ref logic clk, ref logic pin, input logic active, input int cycles);
        automatic logic inactive = ~active;
        @(negedge clk);
        pin = active;
        #0;
        for(int i = 0; i < cycles; i++) begin
            @(posedge clk);
        end
        pin = inactive;
        #0;
    endtask

    // Synchronously triggers the logic bit `pin` to its state `active` and then 
    // asynchronously deactivates the bit to its initial value after `cycles`
    // clock cycles elapse.
    //
    // The trigger will not be applied if `cycles` is set to 0. The signal will
    // deactivate on the falling edge of the `cycles` count clock cycle.
    task automatic sync_on_async_off(ref logic clk, ref logic pin, input logic active, input int cycles);
        automatic logic inactive = ~active;
        if(cycles > 0) begin
            @(posedge clk);
            pin = active;
            #0;
            for(int i = 0; i < cycles; i++) begin
                @(posedge clk);
            end
            @(negedge clk);
            pin = inactive;
        end
    endtask

    task automatic sync_hi_async_lo(ref logic clk, ref logic pin, input int cycles);
        sync_on_async_off(clk, pin, 1'b1, cycles);
    endtask

    // Synchronously triggers the logic bit `pin` to its state `active` and then 
    // synchronously deactivates the bit to its initial value after `cycles`
    // clock cycles elapse.
    //
    // The trigger will not be applied if `cycles` is set to 0. The signal will
    // deactivate on the falling edge of the `cycles` count clock cycle.
    task automatic sync_on_sync_off(ref logic clk, ref logic pin, input logic active, input int cycles);
        automatic logic inactive = ~active;
        if(cycles > 0) begin
            @(posedge clk);
            pin = active;
            #0;
            for(int i = 0; i < cycles; i++) begin
                @(posedge clk);
            end
            pin = inactive;
        end
    endtask

    // Return a string in binary format by reading a logic value from the line `row`.
    function string parse(inout string row);
        automatic string sect = "";
        for(int i = 0; i < row.len(); i++) begin
            if(row[i] == " " || row[i] == "\n") begin
                row = row.substr(i+1, row.len()-1);
                break;
            end
            sect = {sect, row[i]};
        end
        return sect;
    endfunction

    /* events
    
        Data recording procedures to capture events of interest during 
        simulation.
    */

    // The log level type.
    typedef enum {TRACE, DEBUG, INFO, WARN, ERROR, FATAL} tone;

    // Immediate assertion that checks if two logic words `received` and `expected` are equal to each other.
    //
    // Note: https://stackoverflow.com/questions/67714329/systemverilog-string-variable-as-format-specifier-for-display-write
    task assert_eq(input logic[4095:0] received, input logic[4095:0] expected, input string subject);
        if(received == expected) begin
            capture(FD_EVENTS, INFO, "ASSERT_EQ", subject, {"receives ", $sformatf("b'%0b", received), " and expects ", $sformatf("b'%0b", expected)});
        end else begin
            capture(FD_EVENTS, ERROR, "ASSERT_EQ", subject, {"receives ", $sformatf("b'%0b", received), " but expects ", $sformatf("b'%0b", expected)});
        end
    endtask

    // Immediate assertion that checks if two logic words `received` and `expected` are equal to each other.
    task assert_eq_old(inout int fd, input string received, input string expected, input string subject);
        if(received == expected) begin
            capture(fd, INFO, "ASSERT_EQ", subject, {"receives ", received, " and expects ", expected});
        end else begin
            capture(fd, ERROR, "ASSERT_EQ", subject, {"receives ", received, " but expects ", expected});
        end
    endtask

    // Immediate assertion that checks if two logic words `received` and `expected` are not equal to each other.
    task assert_ne(inout int fd, input string received, input string expected, input string subject);
        if(received != expected) begin
            capture(fd, INFO, "ASSERT_EQ", subject, {"receives ", received, " and does not expect ", expected});
        end else begin
            capture(fd, ERROR, "ASSERT_EQ", subject, {"receives ", received, " but does not expect ", expected});
        end
    endtask

    // Checks the logic `flag` is true (1'b1) on the rising edge of `clk` before `cycles` clock cycles elapse.
    task automatic observe(ref logic clk, ref logic flag, input logic active, input int cycles, input string subject);
        automatic int cycle_count = 0;
        automatic int cycle_limit = cycles;

        if (cycle_limit < 0) begin
            @(negedge clk, flag == active);
            return;
        end else begin
            while (cycle_count < cycle_limit) begin
                if (flag == active) begin
                    capture(FD_EVENTS, INFO, "OBSERVE", subject, {"is true after waiting ", $sformatf("%-d", cycle_count), " cycle(s)"});
                    break;
                end
                cycle_count = cycle_count + 1;
                if (cycle_count < cycle_limit) begin
                    @(negedge clk);
                end
            end
        end

        if(cycle_count >= cycle_limit) begin
            capture(FD_EVENTS, ERROR, "OBSERVE", subject, {"fails to be true after waiting ", $sformatf("%-d", cycle_count), " cycle(s)"});
        end
    endtask;

    // Concurrent assertion that checks the behavior of `data` is stable when the condition `flag` is true (1'b1).
    task automatic assert_stbl(ref logic clk, input logic flag, input logic active, input logic[4095:0] data, input string subject);
        static logic[4095:0] last_data[string];
        static int last_flag[string];
        static int cycles[string];
        static int is_stable[string];

        // stay in tracking state
        if (last_flag.exists(subject) == 1 && last_flag[subject] == 1 && flag == active) begin
            // things must remain stable!
            if (last_data[subject] != data && is_stable[subject] == 1) begin
                is_stable[subject] = 0;
                capture(FD_EVENTS, ERROR, "ASSERT_STBL", subject, {"loses stability of ", $sformatf("b'%0b", last_data[subject]), " by changing to ", $sformatf("b'%0b", data), " after ", $sformatf("%-d", cycles[subject]), " cycle(s)"});
            end
            // survived another cycle
            cycles[subject] = cycles[subject] + 1;
        // successfully leave the tracking state
        end else if (last_flag.exists(subject) == 1 && last_flag[subject] == 1 && flag == ~active) begin
            if (is_stable.exists(subject) == 1 && is_stable[subject] == 1) begin
                capture(FD_EVENTS, INFO, "ASSERT_STBL", subject, {"keeps stability at ", $sformatf("b'%0b", last_data[subject]), " for ", $sformatf("%-d", cycles[subject]), " cycle(s)"});
            end
        // try to transition into tracking state
        end else if (last_flag.exists(subject) == 1 && last_flag[subject] == 0 && flag == active) begin
            // $display("*** %s", subject);
            cycles[subject] = 1;
            is_stable[subject] = 1;
        end

        last_data[subject] = data;
        last_flag[subject] = (flag == active) ? 1 : 0;
        
        @(negedge clk);
        #0;
    endtask

    // Concurrent assertion that checks the behavior of `data` is stable when the condition `flag` is true (1'b1).
    task automatic assert_stbl_old(inout int fd, ref logic clk, ref logic flag, ref string data, input string subject);
        automatic logic is_okay = 1'b1;
        automatic logic is_checked = 1'b0;
        automatic string prev_data = "";
        automatic int num_cycles = 0;
        automatic string num_cycles_fmt = "";

        @(posedge clk);

        prev_data = data;
        while(flag == 1'b1) begin
            is_checked = 1'b1;
            if(prev_data != data) begin
                is_okay = 1'b0;
                // capture
                $sformat(num_cycles_fmt, "%-d", num_cycles);
                capture(fd, ERROR, "ASSERT_STBL", subject, {"loses stability of ", prev_data, " by changing to ", data, " after ", num_cycles_fmt, " cycle(s)"});
            end
            @(posedge clk);
            num_cycles = num_cycles + 1;
        end
        if(is_checked == 1'b1 && is_okay == 1'b1) begin
            $sformat(num_cycles_fmt, "%-d", num_cycles);
            capture(fd, INFO, "ASSERT_STBL", subject, {"keeps stability at ", prev_data, " for ", num_cycles_fmt, " cycle(s)"});
        end
    endtask

    // Captures an event during simulation and writes the outcome to the file `fd`.
    // The time when the task is called is recorded in the timestamp.
    task automatic capture(inout int fd, input tone level, input string topic, input string subject, input string predicate = "");
        automatic string result = "";
        automatic string sect = "";
        automatic string time_units = "";

        static int TIMESTAMP_SHIFT = 20;
        static int LOGLEVEL_SHIFT = 10;
        static int TOPIC_SHIFT = 15;

        // determine the simulation's time units
        if(int'(1s) == 1) begin
            time_units = "s";
        end else if(int'(1ms) == 1) begin
            time_units = "ms";
        end else if(int'(1us) == 1) begin 
            time_units = "us";
        end else if(int'(1ns) == 1) begin
            time_units = "ns";
        end else if(int'(1ps) == 1) begin 
            time_units = "ps";
        end else if(int'(1fs) == 1) begin
            time_units = "fs";
        end else begin
            time_units = "";
        end

        // record the time
        $sformat(result, "%0d%s", $time, time_units);
        for(int i = result.len(); i < TIMESTAMP_SHIFT-1; i++) begin
            result = {result, " "};
        end
        result = {result, " "};

        // record the severity 
        if(level == TRACE) begin
            sect = "TRACE";
        end else if(level == DEBUG) begin
            sect = "DEBUF";
        end else if(level == INFO) begin
            sect = "INFO";
        end else if(level == WARN) begin
            sect = "WARN";
        end else if(level == ERROR) begin   
            sect = "ERROR";
        end else if(level == FATAL) begin
            sect = "FATAL";
        end else begin
            sect = "INFO";
        end
        result = {result, sect};

        for(int i = sect.len(); i < LOGLEVEL_SHIFT-1; i++) begin
            result = {result, " "};
        end
        result = {result, " "};

        // record the topic
        sect = "";
        foreach(topic[i]) begin
            if(topic[i] == " ") begin
                sect = {sect, "_"};
            end else begin
                sect = {sect, topic[i]};
            end
        end
        result = {result, sect};

        for(int i = sect.len(); i < TOPIC_SHIFT-1; i++) begin
            result = {result, " "};
        end
        result = {result, " "};

        // record the information about the event
        if(subject != "") begin
            result = {result, subject};
        end

        if(predicate != "") begin
            if(subject != "") begin
                result = {result, " "};
            end
            result = {result, predicate};
        end
        
        $fwrite(fd, {result, "\n"});
    endtask

    /* macros

        A nicer way to use Verb that resembles much of the API style as its
        VHDL counterpart.
    */

// `ifndef VERB
// `define VERB

//     `define capture(LEVEL, TOPIC, SUBJECT, PREDICATE) \
//         capture(FD_EVENTS, LEVEL, TOPIC, SUBJECT, PREDICATE);

//     `define sync_hi_async_lo(CLK, DATA, CYCLES) \
//         sync_on_async_off(CLK, DATA, 1'b1, CYCLES);

//     `define async_hi_sync_lo(CLK, DATA, CYCLES) \
//         async_on_sync_off(CLK, DATA, 1'b1, CYCLES);

//     `define async_lo_sync_hi(CLK, DATA, CYCLES) \
//         async_on_sync_off(CLK, DATA, 1'b0, CYCLES);

//     `define assert_eq(RECV, EXPT, SUBJECT) \
//         begin \
//             automatic string \RECV\ ; \
//             automatic string \EXPT\ ; \
//             $sformat(\RECV\ , "%b", RECV); \
//             $sformat(\EXPT\ , "%b", EXPT); \
//             assert_eq_old(FD_EVENTS, \RECV\ , \EXPT\ , SUBJECT); \
//         end 

//     `define assert_ne(RECV, EXPT, SUBJECT) \
//         begin \
//             automatic string \RECV\ ; \
//             automatic string \EXPT\ ; \
//             $sformat(\RECV\ , "%b", RECV); \
//             $sformat(\EXPT\ , "%b", EXPT); \
//             assert_ne(FD_EVENTS, \RECV\ , \EXPT\ , SUBJECT); \
//         end 

//     `define assert_stbl(CLK, FLAG, DATA, SUBJECT) \
//         `ifndef \DATA\ \
//         `define \DATA\ \
//         string \DATA\ ; \
//         `endif \
//         always @(negedge clk) $sformat(\DATA\ , "%b", DATA); \
//         always assert_stbl_old(FD_EVENTS, CLK, FLAG, \DATA\ , SUBJECT);

//     // Analyzes the next part of the LINE into the logic value for X.
//     `define parse(LINE, X) \
//         $sscanf(parse(LINE), "%b", X);

//     `define observe(CLK, FLAG, CYCLES, SUBJECT) \
//         begin \
//             automatic int cycle_count = 0; \
//             automatic int cycle_limit = CYCLES + 1; \
//             automatic string fmt_cycles; \
//             if(cycle_limit < 0) begin \
//                 @(negedge CLK, FLAG == 1'b1); \
//             end else begin \
//                 while(cycle_count < cycle_limit) begin \
//                     if(FLAG == 1'b1) begin \
//                         $sformat(fmt_cycles, "%-d", cycle_count); \
//                         capture(FD_EVENTS, INFO, "OBSERVE", SUBJECT, {"is true after waiting ", fmt_cycles, " cycle(s)"}); \
//                         break; \
//                     end \
//                     cycle_count = cycle_count + 1; \
//                     if(cycle_count < cycle_limit) begin \
//                         @(negedge CLK); \
//                     end \
//                 end \
//             end \
//             if(cycle_count >= cycle_limit) begin \
//                 $sformat(fmt_cycles, "%-d", CYCLES); \
//                 capture(FD_EVENTS, ERROR, "OBSERVE", SUBJECT, {"fails to be true after waiting ", fmt_cycles, " cycle(s)"}); \
//             end \
//         end

//     `define complete() \
//         complete(FD_EVENTS);

// `endif

endpackage
