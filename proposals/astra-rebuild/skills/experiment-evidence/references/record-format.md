# Optional machine-consumed evidence record

Use an existing project evidence system when available. This format is only for
consumers that need identity/digest checking. The caller supplies an independently
reviewed contract and a dedicated artifact directory. Checksums detect mismatches;
they do not authenticate a run, establish scientific truth or grant authorization.

The contract identifies `version: 1`, `use_id`, `identity` (nonempty strings for
`source`, `build`, `target`, `workload`, `configuration`, `environment`), and a
nonempty `conditions` list. Each condition has `id`, `obligation` (`required`,
`target`, `out-of-scope`), `source`, `criterion` and `method`. An out-of-scope item
also requires `reason`. Do not change required conditions to fit a result.

The record identifies `version: 1`, the same `use_id` and `identity`, the SHA-256
of the exact contract file as `contract_sha256`, and `results`. Each result has
`id`, `status` (`pass`, `fail`, `not-measured`, `not-applicable`), the agreed `method`,
`artifacts` and optional `limits`. An artifact has `path` relative to the dedicated
evidence root and its `sha256`. Absolute paths, traversal and symlinks are rejected.

Every required condition needs a pass with an existing digest-matched artifact.
Missing, not-applicable or unmeasured required conditions fail validation. Optional
targets may remain unmet. Artifact identity must match the intended workload and
target; a caveat cannot make host evidence establish a device condition.

Run `python scripts/validate_record.py CONTRACT.json RECORD.json --evidence-root ARTIFACTS`
from this skill's directory. Keep originals and append corrected records rather
than rewriting a failed historical result. This validator cannot detect a caller
who changes both contract and record: approval and artifact authenticity belong
to the enclosing system, which must also review completeness of the contract.
