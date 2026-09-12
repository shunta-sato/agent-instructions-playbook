# Platform-specific questions

## Android
Check the actual lifecycle owner, dispatcher/thread affinity and cancellation
contract. Do not detach work from a lifecycle merely to make a test pass. Main-thread
blocking, binder callbacks, coroutine cancellation and native ownership can cross
language boundaries; verify the boundary actually present. Background scheduling
and permission restrictions depend on target SDK and OS: inspect project versions
and current platform documentation before prescribing an API.

## ROS 2
Check executor configuration, callback groups, mutual exclusion/reentrancy, timer
and subscription lifetimes, shutdown ordering and bounded queues. A multi-threaded
executor does not alone establish safe parallelism, and a mutually exclusive group
does not prove every external/native access is serialized. Verify the deployed
middleware/version and actual callback ownership rather than a generic ROS label.

## Native tooling
Use project-supported sanitizers/annotations when they can observe the boundary.
Record unsupported targets, instrumentation distortion and schedule coverage.
Treat a race or deadlock diagnosis separately from a throughput benchmark.
