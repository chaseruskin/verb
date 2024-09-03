package godan;

    /* tutils

        Provides test utility functions for testbench simulation. This involves
        reading interface signals, loading expected values, and various 
        simulation-specific tasks.
    */

    // Closes the file `fd` and sets `halt` to true and enters an infinite wait 
    // statement to signal that the simulation is complete.
    task complete(input int fd, output logic halt);
        $fclose(fd);
        halt = 1'b1;
        $finish;
    endtask

    // Generates a half duty cycle clock `clk` with a period of `period` that
    // is continuously driven until `halt` is set to true.
    task spin_clock(output logic clk, input time period, input logic halt);
        if(halt == 1'b1) begin
            wait(0);
        end else begin
            clk = ~clk;
            #(period/2);
        end
    endtask

    // Return a string in binary format to drive a logic value from the line `row`.
    function string drive(inout string row);
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

    // Return a string in binary format by reading a logic value from the line `row`.
    function string load(inout string row);
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

    // Asserts that two logic words `received` and `expected` are equal to each other.
    task assert_eq(inout int fd, input string received, input string expected, input string subject);
        if(received == expected) begin
            capture(fd, INFO, "ASSERT_EQ", subject, {"receives ", received, " and expects ", expected});
        end else begin
            capture(fd, ERROR, "ASSERT_EQ", subject, {"receives ", received, " but expects ", expected});
        end
    endtask

    // Asserts that two logic words `received` and `expected` are not equal to each other.
    task assert_ne(inout int fd, input string received, input string expected, input string subject);
        if(received != expected) begin
            capture(fd, INFO, "ASSERT_EQ", subject, {"receives ", received, " and does not expect ", expected});
        end else begin
            capture(fd, ERROR, "ASSERT_EQ", subject, {"receives ", received, " but does not expect ", expected});
        end
    endtask

    // Captures an event during simulation and writes the outcome to the file `fd`.
    // The time when the task is called is recorded in the timestamp.
    task capture(inout int fd, input tone level, input string topic, input string subject, input string predicate = "");
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
        $sformat(result, "%-d%s", $time, time_units);
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
            sect = "TRACE";
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

endpackage
