---
description: "Ivan Anishchuk's Ethereum Protocol Fellowship cohort-seven work: biweekly dev updates and notes on formal verification for Ethereum."
---

# Ethereum Protocol Fellowship, cohort seven

I am Ivan Anishchuk, a cohort-seven fellow in the
[Ethereum Protocol Fellowship](https://github.com/eth-protocol-fellows/cohort-seven).
My fellowship work is formal verification for Ethereum. I write machine-checked
proofs about the protocol so client teams have specifications they can check, not
only read.

This site is the public record of that work. It carries my biweekly dev updates
and notes on the project, and it keeps a stable home after the fellowship ends.

## The work

The current focus is [etheorem](https://github.com/etheorem/etheorem), Ethereum's
consensus spec written in Lean 4: one artifact that runs, passes the official test
vectors, and carries machine-checked proofs. I work the consensus layer, everything
above the wire format, from arithmetic and structural invariants up through
merkleization, the validator shuffle, and fork choice.

[Read more about the project.](project.md)

## Follow along

- **[Updates](updates/index.md)** for biweekly dev updates and project news.
- **[Project](project.md)** for the scope, goals, and links of the
  formal-verification work.
- **[About](about.md)** for who I am, the fellowship, and how to reach me.

Out on the wider web:

- [etheorem](https://github.com/etheorem/etheorem), the Lean 4 formalization of
  Ethereum's consensus spec.
- [EPF cohort seven](https://github.com/eth-protocol-fellows/cohort-seven), the
  fellowship program repo and its dev-update log.
