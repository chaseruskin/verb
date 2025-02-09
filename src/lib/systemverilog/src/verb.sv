package verb;

    // The default file to write to when events occur during simulation
    int FD_EVENTS = start("events.log");

    /* UTILITY

        Provides test utility functions for testbench simulation. This involves
        reading interface signals, loading expected values, and various 
        simulation-specific tasks.
    */

    // Creates the file with the given `name` to prepare for simulation logging.
    function automatic int start(input string name);
        int fd = $fopen(name, "w");
        return fd;
    endfunction

    // Closes the event log file and ends the simulation completely.
    task finish(int n=0);
        $fclose(FD_EVENTS);
        $finish(n);
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

    // Synchronously set `pin` high, then asynchronously set `pin` low.
    task automatic sync_hi_async_lo(ref logic clk, ref logic pin, input int cycles);
        sync_on_async_off(clk, pin, 1'b1, cycles);
    endtask

    // Synchronously set `pin` low, then asynchronously set `pin` high.
    task automatic sync_lo_async_hi(ref logic clk, ref logic pin, input int cycles);
        sync_on_async_off(clk, pin, 1'b0, cycles);
    endtask

    // Asynchronously set `pin` high, then synchronously set `pin` low.
    task automatic async_hi_sync_lo(ref logic clk, ref logic pin, input int cycles);
        async_on_sync_off(clk, pin, 1'b1, cycles);
    endtask

    // Asynchronously set `pin` low, then synchronously set `pin` high.
    task automatic async_lo_sync_hi(ref logic clk, ref logic pin, input int cycles);
        async_on_sync_off(clk, pin, 1'b0, cycles);
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

    /* EVENTS
    
        Data recording procedures to capture events of interest during 
        simulation.
    */

    // The log level type.
    typedef enum {TRACE, DEBUG, INFO, WARN, ERROR, FATAL} tone;

    // Captures an event during simulation and writes the outcome to the file `fd`.
    //
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

    // Assertion that checks if two logic words `received` and `expected` are equal to each other.
    //
    // Note: https://stackoverflow.com/questions/67714329/systemverilog-string-variable-as-format-specifier-for-display-write
    task assert_eq(input logic[4095:0] received, input logic[4095:0] expected, input string subject);
        if(received == expected) begin
            capture(FD_EVENTS, INFO, "ASSERT_EQ", subject, {"receives ", $sformatf("b'%0b", received), " and expects ", $sformatf("b'%0b", expected)});
        end else begin
            capture(FD_EVENTS, ERROR, "ASSERT_EQ", subject, {"receives ", $sformatf("b'%0b", received), " but expects ", $sformatf("b'%0b", expected)});
        end
    endtask

    // Assertion that checks if two logic words `received` and `expected` are not equal to each other.
    task assert_ne(input logic[4095:0] received, input logic[4095:0] expected, input string subject);
        if(received != expected) begin
            capture(FD_EVENTS, INFO, "ASSERT_NE", subject, {"receives ", $sformatf("b'%0b", received), " and does not expect ", $sformatf("b'%0b", expected)});
        end else begin
            capture(FD_EVENTS, ERROR, "ASSERT_NE", subject, {"receives ", $sformatf("b'%0b", received), " but does not expect ", $sformatf("b'%0b", expected)});
        end
    endtask

    // Assertion that checks that the behavior of `data` is stable while the condition `flag` is true (1'b1).
    task automatic assert_stbl(input bit flag, input logic[4095:0] data, input string subject);
        static logic[4095:0] last_data[string];
        static int last_flag[string];
        static int cycles[string];
        static int is_stable[string];

        #0;
        // stay in tracking state
        if (last_flag.exists(subject) == 1 && last_flag[subject] == 1 && flag == 1'b1) begin
            // things must remain stable!
            if (last_data[subject] != data && is_stable[subject] == 1) begin
                is_stable[subject] = 0;
                capture(FD_EVENTS, ERROR, "ASSERT_STBL", subject, {"loses stability of ", $sformatf("b'%0b", last_data[subject]), " by changing to ", $sformatf("b'%0b", data), " after ", $sformatf("%-d", cycles[subject]), " cycle(s)"});
            end
            // survived another cycle
            cycles[subject] = cycles[subject] + 1;
        // successfully leave the tracking state
        end else if (last_flag.exists(subject) == 1 && last_flag[subject] == 1 && flag == 1'b0) begin
            if (is_stable.exists(subject) == 1 && is_stable[subject] == 1) begin
                capture(FD_EVENTS, INFO, "ASSERT_STBL", subject, {"keeps stability at ", $sformatf("b'%0b", last_data[subject]), " for ", $sformatf("%-d", cycles[subject]), " cycle(s)"});
            end
        // try to transition into tracking state
        end else if (last_flag.exists(subject) == 1 && last_flag[subject] == 0 && flag == 1'b1) begin
            // $display("*** %s", subject);
            cycles[subject] = 1;
            is_stable[subject] = 1;
        end

        last_data[subject] = data;
        last_flag[subject] = (flag == 1'b1) ? 1 : 0;
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

endpackage
