# Events

An _event_ is a thing of importance that takes place during hardware simulation. Events are _captured_ during hardware simulation by being written to a log file, typically called "events.log".

There are functions available in the HW libraries for event logging; see the `events` package for event logging functions such as `capture(...)`, `assert_eq(...)`, `monitor(...)`, and `stabilize(...)`.

## Event log file format

Each event captured during simulation is placed on its own line in the log file. 

Each captured event uses the following pattern:

```
<timestamp> <severity> <topic> <comment>
```

Example:
```
180000000fs         INFO      ASSERT_EQ      sum receives 0110 and expects 0110
```

### Timestamp

The timestamp is the time at which the particular event was captured. The value will not include any spaces and may include the time units as a suffix.

Example:
```
180000000fs
```

### Severity

The severity is the importance of the captured event. It can only be one of the following values: TRACE, DEBUG, INFO, WARN, ERROR, FATAL.

Example:
```
INFO
```

By default, any events that are of TRACE, DEBUG, or INFO importance are considered _OKs_. Any events that are of WARN, ERROR, or FATAL importance are considered _failures_.

### Topic

The topic is the high-level thing that is happening in the captured event. The value will not include any spaces and is typically the function name that was called that captured the event.

Example:
```
ASSERT_EQ
```

### Comment

The comment is low-level information that is important to this capture event. It is composed of two values: a subject and a predicate. 

```
<subject> <predicate>
```

The comment is typically discarded during analysis by Vertex and is mainly for the benefit of the user.

Example:
```
sum receives 0110 and expects 0110
```