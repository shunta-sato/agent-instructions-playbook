# review-modularity

Review the selected diff/files focusing on modularity.

Output:
- Where cohesion got worse (mixed responsibilities)
- Where coupling increased (flags, large context objects, leaking outer types inward)
- Boundary violations (core depends on UI/DB/framework types)
- Minimal refactor suggestions to localize change

Use “worst-level” evaluation: if a unit mixes levels, report the lowest level you see.
