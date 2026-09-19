# Shared contracts

Versioned JSON Schemas use Draft 2020-12. Phase 1 contains only local build metadata; it does not freeze the future agent wire protocol. Valid and invalid fixtures are checked by the Python contract tests. Minor protocol changes must be additive; required-field/semantic changes require a new major directory and compatibility tests.

`fixtures/challenges/` reserves the canonical Ed25519 challenge fixtures. Before Phase 3, review and freeze exact byte encoding, domain separation, public keys, signatures, positive/negative vectors, and Python/Go verification parity. No signing implementation may precede these fixtures.
