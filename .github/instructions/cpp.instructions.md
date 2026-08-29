---
applyTo: "**/*.{h,hpp,hh,hxx,cpp,cc,cxx}"
---

# C++ instructions

## Header contracts

Use Doxygen for changed public/protected declarations and other stable contracts
consumed outside the implementation unit. Document applicable semantics such as
parameters, return/error behavior, ownership, lifetime, thread-safety, units,
ranges, and preconditions.

Private declarations need documentation only for a non-obvious invariant,
hazard, unit, ownership rule, or maintenance contract. Do not add boilerplate to
each member merely because a header was touched.

## Implementation comments

Comments explain constraints, rejected alternatives, hazards, or external
requirements that code and tests cannot express. Do not narrate each paragraph,
routine call, or I/O operation.

## Literals

Name domain-specific, protocol, timing, size, retry, or policy literals when the
meaning is not evident locally or must remain consistent. Trivial local values
and conventional sentinels need no audit record.

## Scope

Apply readability changes to the current diff and its direct contract. Do not
expand a feature into a general comment, naming, or constant-conversion cleanup.
