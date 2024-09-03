package godan;

    typedef enum {TRACE, DEBUG, INFO, WARN, ERROR, FATAL} tone;

    // Sets `halt` to true and enters an infinite wait statement to signal 
    // that the simulation is complete.
    task complete(output logic halt, input int fd);
        halt = 1'b1;
        $fclose(fd);
        $finish;
    endtask

    // Generates a half duty cycle clock `clk` with a period of `period` that
    // is continuously driven until `halt` is set to true.
    task spin_clock(output logic clk, input time period, input logic halt);
        static logic tick;
        if(halt == 1'b1) begin
            wait(0);
        end else begin
            clk = tick;
            #(period/2);
            tick = ~tick;
        end
    endtask


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


    task assert_eq(inout int fd, input string received, input string expected, input string subject);
        if(received == expected) begin
            capture(fd, INFO, "ASSERT_EQ", subject, {"receives ", received, " and expects ", expected});
        end else begin
            capture(fd, ERROR, "ASSERT_EQ", subject, {"receives ", received, " but expects ", expected});
        end
    endtask


    task capture(inout int fd, input tone level, input string topic, input string subject, input string predicate = "");
        automatic string result = "";
        automatic string sect = "";

        static int TIMESTAMP_SHIFT = 20;
        static int LOGLEVEL_SHIFT = 10;
        static int TOPIC_SHIFT = 15;

        // record the time
        $sformat(result, "%-d%s", $time, get_time_units());
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


    function string get_time_units();
        if(int'(1s) == 1) begin
            return "s";
        end else if(int'(1ms) == 1) begin
            return "ms";
        end else if(int'(1us) == 1) begin 
            return "us";
        end else if(int'(1ns) == 1) begin
            return "ns";
        end else if(int'(1ps) == 1) begin 
            return "ps";
        end else if(int'(1fs) == 1) begin
            return "fs";
        end else begin
            return "";
        end
    endfunction;

endpackage