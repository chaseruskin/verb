# Coverage

When verifying hardware, not only is checking _what_ the design generated as outputs important, but also checking _how_ the design generated those outputs is just as important. This tracking of knowledge in _how_ the design reached a set of outputs is known as _coverage_.

### The importance of coverage

For example, consider we are testing a hardware addition unit. If we run 1,000 test cases and they are all correct, we may be led to believe our design is working perfectly! However, if we discover 500 of these test cases are testing 0+0 = 0 and the remaining 500 test cases are testing 0+1 = 1, I would not be so confident to claim the design is working properly. There are so many untested scenarios that we need to run more tests! This example shows the importance of not just making sure _what_ the design outputs is correct, but also making sure _how_ the test cases sufficiently cover the design's input/state space.

### Types of coverage

There are various forms of coverage. One form of coverage is _code coverage_, which involves tracking the actual lines of code that have been executed during testing. Another form of coverage is _functional coverage_, which involves tracking a set of _scenarios_ that have occurred during testing. We define a _scenario_ as a sequence of events that are of interest that set the design into a particular state.

Currently, Vertex only supports functional coverage. Users define coverage goals according to a design's coverage specification through coverage nets.

## Coverage Nets

_Coverage nets_ allow the user to specify the coverage scenarios in software by determining how the design can reach a particular scenario and what the design's state should be when that scenario occurs.

The following coverage nets are available in Vertex:

- `CoverPoint`: Scenarios involving a single state

Example scenario: Overflow bit being asserted.

- `CoverRange`: Scenarios involving an interval of continuous states

Example scenario: All the possible values for a 8-bit input (0-255).

- `CoverGroup`: Scenarios involving multiple states

Example scenario: The minimum and maximum possible values for a 4-bit input (0 and 15).

- `CoverCross`: Scenarios involving the cross product between two or more coverage nets

Example scenario: All possible combinations of values for two 8-bit inputs (0-255 x 0-255).

## Coverage-driven test generation (CDTG)

Randomness is good for verification- it increases the confidence in your design that it is robust against all kinds of inputs. However, randomness without constraints may make it difficult for complex designs to enter coverage scenarios in order to meet coverage in as reasonable number of test vectors. Therefore, a form of constrained randomness is ideal for balancing the robustness factor of a design as well as meeting all coverage goals.

_Coverage-driven test generation_ (CDTG) is a form of constrained randomness that uses the knowledge of the existing coverage nets to generate the next random test vector within the constraints of advancing toward a currently unmet coverage goal.

Vertex supports this form of constrained random test generation by maintaining a list of all the known coverage nets during modeling and assigning the inputs of the model instance with random values that would advance a currently unmet coverage goal.

## Relating fishing to coverage - an analogy

You can think of functional coverage as fishing in a large open sea. We will first tell the story, and then relate it back to functional coverage.

### Fishing

Imagine you are the fisherman for your town. Recently you found an old map of an unexplored sea detailiing the locations in the sea of where to find fish, the types of fish, and quantities of fish. This map will be very valuable to your town if you are able to prove that its information is indeed accurate. With the old map as your guide, you embark on your quest.

First, you craft specially designed nets for each location marked on the map to ensure you catch the right types of fish and their corresponding amounts.

Second, you climb aboard your boat and carefully steer it in the right directions to reach the marked locations on the map.

Upon reaching a marked location, you cast that location's specially crafted net. You hope to reach your goal at each marked location by catching the correct amounts and correct types of fish.

After achieving the goals at each marked location in the sea, you return home to tell your town about the successful quest and that the old map is true!

### Coverage

There are many parallels between our fishing story and the verification process using functional coverage.

The entire state space of the design can be considered the large unexplored sea. It can be very daunting to try to characterize the entire sea without any form of guidance.

Your main source of guidance during the fishing expedition was the _old map_, which can be considered the _coverage specification_ in the verification process. The coverage specification details the desired scenarios and how many times they should occur without failure during testing. Specifying _what_ you would like to cover is typically good practice before trying to cover everything, which at many times is impractical for complex designs.

With the knowledge of what locations in the sea are important, you then create your nets for each location. This is the same as using the knowledge of which coverage scenarios are important to then create _coverage nets_, which formalize the particular scenario in software, how to reach that scenario, and what the design's state should look like during the scenario.

The remaining steps, reaching a marked location and casting the net, may be hard to translate to software. That's where Vertex and coverage-driven test generation shines. CDTG essentially steers your boat automatically (with some degree of randomness) and then casts the correct the net once it arrives at the given scenario. Using CTDG can automate the task of arriving at coverage scenarios for currently unmet coverage goals.

Once all coverage goals are met, it is sufficient to say there are no more inputs required to be tested and testing can conclude. At this point, if all tests generated their correct expected values, then the design is successfully verified. Woo-hoo! Time to return home and tell everyone in your town about functional coverage.