# Research claims

ledger-head: fceeeb82bd1e2f6e7e54a651da59dfcb89478d571e6a68723ea5a53c442f7da4

## C-0001
Observed once under configuration CPython 3.13.13; N=20000 int list; sorted base + 1% random index-pair swaps (200 swaps); seed=20260712; quicksort=textbook recursive Hoare-style partition, first element as pivot, run on a dedicated thread with 512MiB C stack and recursion limit raised to 200000 to avoid a RecursionError/stack crash from the ~N-deep unbalanced recursion this input shape induces: textbook first-element-pivot recursive quicksort wall-time vs built-in sorted() wall-time on nearly-sorted input (ratio degrades).
evidence: E-0001
sources: experiments/sort-degradation-probe/probe.py
