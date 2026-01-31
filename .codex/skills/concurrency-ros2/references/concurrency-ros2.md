# ROS 2 concurrency reference

Use this when working with `rclcpp` or `rclpy` nodes, executors, callback groups, services, actions, or timers.

## Core concepts

### Callback groups
- **MutuallyExclusive:** callbacks in the group do not run concurrently.
- **Reentrant:** callbacks in the group may run concurrently (unsafe unless code is thread-safe).

### Executors vs callback groups
- The **executor** decides which callbacks to run and on which threads.
- **Callback groups** define concurrency rules *within* a node.
- `SingleThreadedExecutor` runs callbacks sequentially; `MultiThreadedExecutor` runs callbacks concurrently where allowed by callback groups.

### Deadlock rule (mandatory)
If a callback makes **synchronous** service/client calls, the called client/service must be in a **different callback group** (or the group must be **Reentrant**). Otherwise, the executor can deadlock by waiting on itself.

## Recommended patterns

- **Worker Thread:** offload heavy compute or blocking I/O.
- **Producer–Consumer queue:** move work from callback to worker with a bounded queue.
- **Two-Phase Termination:** clean shutdown for nodes and workers.

## Minimal skeletons

### Callback groups and binding

```cpp
auto group_main = node->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
auto group_blocking = node->create_callback_group(rclcpp::CallbackGroupType::Reentrant);

rclcpp::SubscriptionOptions options;
options.callback_group = group_main;
auto sub = node->create_subscription<Msg>("topic", qos, cb, options);

rclcpp::ServiceOptions svc_options;
svc_options.callback_group = group_blocking;
auto svc = node->create_service<Srv>("svc", handler, svc_options);
```

### Offload work with bounded queue

```cpp
// Enqueue in callback
queue.try_push(work_item); // drop or backpressure on full

// Worker loop
while (running) {
  if (queue.try_pop(item)) {
    process(item);
  }
}
```

### Two-phase termination (shutdown)

```cpp
// Phase 1: stop accepting
running = false;

// Phase 2: drain and join
queue.close();
worker.join();
```
