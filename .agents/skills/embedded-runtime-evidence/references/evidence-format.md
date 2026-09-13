# Optional integrity manifest, schema version 1

This is a machine-consumed format only for users of `scripts/verify_evidence.py`.
It does not make an extra document mandatory in ordinary development.

The contract is an object with `schema_version: 1` and a nonempty `requirements` list.
Each item has a unique string `id`, `obligation` (`required` or `target`), nonempty
`criterion` and `source`, and the five nonempty identity strings `candidate`, `target`,
`workload`, `configuration`, `method`.

Evidence has `schema_version: 1` and a `results` list. Each result has a matching unique
`id`, those same five identities, `status` (`pass`, `fail`, `not-measured`), and optional
`artifacts`: a list of `{ "path": "relative/file", "sha256": "64 lowercase hex digits" }`.
A passing result needs at least one artifact. Paths must be within the explicit evidence
root, with no symlinks or traversal. Required conditions need passing results; absent or
unmet optional targets are permitted. Malformed or misleading optional evidence is not.

Run the script with `--contract CONTRACT.json --evidence EVIDENCE.json --root EVIDENCE_DIR`.
Exit 0 means identities and digests are internally consistent, not that a measurement
happened or its method/threshold is valid. The reviewer must inspect actual raw evidence
and applicability. The manifest cannot certify a fabricated but internally consistent run.
