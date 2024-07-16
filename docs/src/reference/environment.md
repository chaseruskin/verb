# Environment Variables

A design model written in software may require data from external sources, such as the testbench's interface or the randomness seed. To communicate these values to any design model in any programming language, Verb uses environment variables.

The following environment variables are supported:  
- `VERB_TB` — The targeted testbench's interface in JSON.
- `VERB_DUT` - The targeted design-under-test's interface in JSON.
- `VERB_RAND_SEED` - The random seed value.
- `VERB_EVENTS_FILE` - Path to expect the events log.
- `VERB_COVERAGE_FILE` - Path to expect the coverage report.
- `VERB_LOOP_LIMIT` - Maximum number of main loop iterations to perform before forcing a break.