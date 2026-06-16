---
description: "The formal-verification work of Ivan Anishchuk's EPF cohort-seven fellowship, currently a Lean 4 formalization of Ethereum SSZ (etheorem)."
---

# The project

My fellowship project is formal verification for Ethereum. The goal is to take
parts of the protocol that client teams treat as a specification and prove their
properties in a machine-checked proof assistant. The specification then becomes
something you can run a checker against.

## Current focus: SSZ in Lean 4

The active work is [etheorem](https://github.com/etheorem/etheorem), a
[Lean 4](https://lean-lang.org/) formalization of Simple Serialize (SSZ). SSZ is
the serialization and Merkleization scheme the Ethereum consensus layer is built
on. Beacon-chain state, blocks, and the hashes that tie them together all pass
through it, so a precise account of how SSZ behaves is useful to every consensus
client.

The formalization follows the consensus-specs SSZ definition as its source of
truth. Where the prose specification leaves room for interpretation, the Lean
version has to commit to a single reading, which surfaces the ambiguities worth
raising upstream.

## Scope

This is the framing as it stands at the start of the fellowship, and it will
sharpen as the work proceeds. The biweekly [updates](updates/index.md) track what
got built, the problems that came up, and how I worked through them.

## Links

- [etheorem](https://github.com/etheorem/etheorem), the Lean 4 SSZ formalization.
- [EPF cohort seven](https://github.com/eth-protocol-fellows/cohort-seven), the
  fellowship program and its dev-update log.
- [Consensus-specs SSZ](https://github.com/ethereum/consensus-specs/blob/master/ssz/simple-serialize.md),
  the serialization specification the work follows.
