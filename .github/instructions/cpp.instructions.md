---
applyTo: "**/*.{h,hpp,hh,hxx,cpp,cc,cxx}"
---

# C++ instructions (readability + maintainability)

## Header documentation (`.hpp` / `.h`)

Doxygen documentation is mandatory for this repository.

- Add Doxygen comments for **all declarations**, including **private** members:
  - classes/structs
  - methods
  - member fields
  - constants
- For functions/methods, include:
  - what it does
  - parameter meaning (`@param`)
  - return meaning (`@return`, or state explicitly that there is no return value)
  - notable failure modes (exceptions / error returns) when applicable
- For fields/constants, include:
  - meaning
  - unit (if any)
  - allowed range or allowed set of values

If you generate docs and want private members to appear, configure Doxygen accordingly (e.g., `EXTRACT_PRIVATE = YES`).

## Source documentation (`.cpp`)

- **Paragraph comments** must explain one of:
  - intent (why this approach)
  - assumptions / invariants
  - pitfalls / failure modes
- Do not write comments that restate what the code already says.

## Magic values

- Avoid “magic values” (numeric/string literals that encode meaning).
- Use `constexpr`, `enum class`, or named constants.
- Exceptions are allowed only for trivial literals where meaning is universally obvious, and must include a short reason.

## Required audits when changing `.cpp`

If the change touches `.cpp`:

- **Comment intent audit**: list changed/added comments and classify each as intent/assumption/pitfall. Rewrite or delete anything that cannot be classified.
- **Magic value audit**: list newly introduced literals and show the named constant/enum replacement (or justify the exception).
