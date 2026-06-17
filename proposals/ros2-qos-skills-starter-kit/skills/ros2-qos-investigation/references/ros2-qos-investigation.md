# ROS 2 QoS investigation reference

## A) Investigation contract

A ROS 2 QoS investigation should make the implementation path explicit and keep evidence separate from assumptions.

For Reliability QoS, start from the ROS-facing QoS API and follow the value until it becomes DDS and RTPS behavior. Treat application callback delivery as a separate boundary from RTPS reliable delivery.

## B) Source trace spine

| Layer | Typical repository | What to verify |
| --- | --- | --- |
| ROS client API | `rclcpp`, `rclpy` | QoS construction and defaults |
| ROS C layer | `rcl` | publisher/subscription creation options |
| RMW abstraction | `rmw` | `rmw_qos_profile_t` and enum values |
| Fast DDS RMW | `rmw_fastrtps` | ROS QoS to Fast DDS DDS QoS mapping |
| Type support | `rosidl_typesupport_fastrtps` | serialization path when payload matters |
| DDS Entity layer | `Fast-DDS` | DataWriter/DataReader QoS and endpoint attributes |
| RTPS endpoint layer | `Fast-DDS` | writer/reader creation and reliability kind |
| RTPS reliable protocol | `Fast-DDS` | heartbeat, ACKNACK, NACK response, proxy state, resend behavior |
| History and cache | `Fast-DDS` | WriterHistory, ReaderHistory, cache changes, resource limits |
| Application delivery | ROS 2 executor/subscription path | callback delivery, queues, and backpressure |

## C) Reliability QoS questions

1. Where is the ROS policy value set?
2. Where is `SYSTEM_DEFAULT` or profile fallback resolved?
3. Can XML, environment variables, or middleware defaults change the expected QoS?
4. Where is Reliable vs Best Effort mapped to Fast DDS QoS?
5. Where does DDS QoS become RTPS endpoint attributes?
6. Which writer/reader implementation is used for the scoped path?
7. Which object owns per-reader or per-writer sequence-number state?
8. Which history/cache object stores data that can be resent?
9. What causes heartbeat emission?
10. What causes ACKNACK or NACK response handling?
11. What evidence confirms retransmission behavior?
12. What is the boundary between RTPS delivery and ROS callback execution?
13. Does the claim still hold for intra-process, DataSharing, or same-host paths?
14. What remains unknown without runtime evidence?

## D) Evidence levels

| Evidence level | Meaning |
| --- | --- |
| `source-trace` | File/function/ref shows the implementation path |
| `test` | reproducible test or minimal program confirms behavior |
| `runtime-log` | logs or traces from the scoped run confirm behavior |
| `packet-capture` | RTPS packets confirm protocol behavior for the scoped transport |
| `benchmark` | measured latency, throughput, or resource result confirms a cost claim |
| `external-doc` | external documentation supports semantics but is not implementation proof |
| `assumption` | plausible but unverified |
| `unknown` | investigation has not reached this point |

## E) Discussion packet

Include the claim under discussion, supporting trace, contradictory evidence, assumptions, next probes, and reviewer decisions requested.
