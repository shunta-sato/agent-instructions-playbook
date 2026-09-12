# ROS 2 callback and executor boundaries

Identify the actual ROS distribution, callback groups, executor, blocking calls and
ownership of shared state. A synchronous wait for a callback that cannot be scheduled
under the current group/executor arrangement can prevent progress. More executor threads
alone are not proof that the dependency can run.

Map which callbacks may overlap and which state they share. Distinguish mutual exclusion,
reentrancy, message ordering, queueing/QoS effects and shutdown behavior. Check timers,
services, actions and subscription paths that can contend for the same worker or lock.

Use API forms supported by the project's distribution. Reproduce a relevant interleaving
with bounded deterministic coordination where feasible; arbitrary sleeps are weak proof.
Verify cancellation and shutdown do not strand work or permit late use of destroyed state.
