---
applyTo: "**/*.{h,hpp,cc,cpp,cxx}"
---
Respect the target project's C++ style and ABI/ownership constraints. Do not use a
language-file match to trigger unrelated architecture, function-ledger or quality
workflows. Put non-obvious lifetime, concurrency and ABI constraints where callers
need them; avoid duplicating the implementation in comments.
