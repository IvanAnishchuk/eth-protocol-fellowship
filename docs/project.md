---
description: "etheorem, Ethereum's consensus spec in Lean 4: machine-checked proofs for merkleization, the validator shuffle, and fork choice, Ivan Anishchuk's EPF cohort-seven project."
---

# etheorem: machine-checked proofs for Ethereum's consensus spec, in Lean 4

My EPF cohort-seven project. etheorem is Ethereum's consensus spec written in Lean 4, as
one artifact that runs, passes the official test vectors, and carries machine-checked
proofs. I work the consensus layer: arithmetic and structural invariants, merkleization,
the validator shuffle, fork choice and finality, plus keeping conformance green as the
forks move.

It is a joint proposal with Raj Gill ([@irajgill](https://github.com/irajgill)), split by
layer. He takes SSZ, I take everything above it, and this page is about my half. Our
mentor is Leo Lara ([@leolara](https://github.com/leolara)), who wrote etheorem and
proposed it upstream as a cohort-seven project idea.

One disambiguation, since it comes up every time. "Lean 4" here is the theorem prover, not
the lean chain and not Beam. Different Lean, same word. etheorem formalizes the spec
running on mainnet now, plus the forks next in line.

## What it's for

Ethereum's consensus layer has one spec, executable Python, and every client is expected
to conform to it. Conformance gets checked with test vectors generated from that spec.
Clients run them, they go green, that's the evidence. But vectors only cover the cases
somebody thought to generate, so the properties the protocol actually rests on stay
checked by example and unproven in general.

etheorem is that same spec in Lean 4, one artifact you can run, test and prove. It
executes. It passes the official vectors at Fulu and Gloas. And the definitions carrying
the proofs are the definitions that run, so a proof and a passing vector describe the same
spec instead of drifting apart in two repos, which is the usual failure mode.

The spec has been moving in this direction for years. The Yellow Paper set the pattern
on the execution side, prose and mathematics that clients read and reimplemented.
Consensus skipped that stage, it's been executable Python since Phase 0, and execution
caught up later with [EELS](https://github.com/ethereum/execution-specs). Each step more
runnable, and more directly testable against what clients ship. Lean is the next one, it
still runs and still passes the vectors, and you can prove things about it on top of that.

Lean 4 in particular because the spec and its proofs are the same language. No separate
model to keep in sync with the spec, which is where a lot of verification effort usually
goes. There's a live Ethereum-adjacent Lean ecosystem now too, Nethermind's EVMYulLean on
the execution side, Nyx's leanSpec on consensus, so idioms and tooling carry over.

## What's been proved already, and what hasn't

Prior formal verification of the beacon chain is real and partial.

The ConsenSys Dafny work (TACAS 2022, archived read-only in 2026) proved SSZ round-trip
and injectivity for basic types, bitlists and bitvectors, plus state-transition refinement
and fork-choice store invariants. Not the mixed-field containers the beacon chain actually
serializes, though. Overflow bounds were assumed via axiom lemmas instead of discharged,
merkleization stayed differential-tested with `hash()` uninterpreted, and there's no real
shuffle in it. Phase 0 only.

Runtime Verification proved the deposit contract's incremental Merkle tree in K (CAV
2020), and Gasper accountable safety in Coq on an abstract model. Their K state-transition
model was conformance-tested but never proved. Apalache/TLA+ bounded model-checked 3SF
accountable safety, which stops short of deductive proof.

All real work, none of it on the protocol as deployed in 2026. There's Lean 4 work next
door, Nyx's `formal-leanSpec`, active and good, but it follows the lean-Ethereum spec
instead of the one on mainnet. So as far as we can tell the current production consensus
spec had no Lean 4 formalization before this one.

Four things nobody has proved anywhere: serialization total over the codec, merkle-branch
completeness, a real validator shuffle, and merkleization over a *verified* hash instead
of an uninterpreted one. That last is why etheorem is the right place to do this. It
already carries a pure-Lean SHA-256 and Poseidon2 proofs on the crypto side, and roughly
65 SSZ theorems on the serialization side, all with an auditable axiom footprint. A
verified hash is what lets merkleization close against something concrete, where both
earlier efforts had to assume one.

## My half

etheorem is an existing upstream project with contributors beyond the two of us, so we're
contributors here, not owners. The fellowship work is one thing, the proofs.

Mine is the consensus layer, everything above the wire format, ordered by rising
difficulty so partial progress still counts. Underneath me Raj is making SSZ's three
central serialization theorems total over the codec, so they hold for every type the spec
serializes and not just most of them. The two halves meet at merkleization, where my
proofs consume his results as an interface. That dependency runs one way, which is why
this is one project with two sides and not two projects sharing a repo.

The easy tier is arithmetic and structural invariants, where the earlier efforts already
charted the path. `increaseBalance` never wraps, total balance stays under 2^64, validator
and balance lists stay in lockstep across the state transition, slot and epoch
monotonicity, length preservation. None of it is difficult. It establishes the proof
patterns the harder tiers build on.

Merkleization is next. `isValidMerkleBranch` is the check that a piece of data really sits
under a given root, the one every light client and every deposit proof leans on. What gets
proved is completeness: an honest inclusion proof always passes the verifier. Take a
well-formed tree, take the honest opening at any index, hand both to the checker, it
accepts. Every tree, every index, no test vectors involved.

```lean
theorem isValidMerkleBranch_complete_sha256Spec
    {n : Node} {depth : Nat}
    (hp : IsPerfect n depth) (index : Nat) :
    letI : HasherTag := pureHasherTag
    isValidMerkleBranch (honestLeaf n depth index)
        (honestBranch Sha256Spec n depth index)
        depth index
        (bytesToRoot (Node.merkleRoot Sha256Spec n))
      = true
```

`#print axioms` on it gives the Lean kernel trio and nothing else, zero new axioms, zero
`sorry`. The "combine returns 32 bytes" fact is a discharged hypothesis, not an
assumption. The footprint is the part that matters, a proof resting quietly on five extra
axioms doesn't say much. It also grounds in etheorem's pure-Lean SHA-256 instead of an
abstract hash, which is what makes it more than an exercise: the earlier efforts left the
hash uninterpreted and could only differential-test around it.

Behind that sits the cached Merkle tree agreeing with the spec root, and a
generalized-index library carrying the same completeness argument out from deposits to the
branches real consumers actually open, the ones a light client verifies a header against
and the blob and data-column sidecar inclusion proofs.

Then the shuffle. `computeShuffledPermutation` is a true permutation, with its committee
cluster behind it. The flagship, and the only genuinely greenfield piece, nobody has
proved a real beacon-chain shuffle. It's also where I expect to slip, which is why
November is buffer.

Fork choice and finality is the stretch tier: store invariants, FOCIL inclusion-list
validity on the Heze layer once it lands, and a start on Casper FFG accountable safety.

Conformance sits underneath all of it. etheorem passes the official
[consensus-spec-tests](https://github.com/ethereum/consensus-spec-tests) today, and
keeping it passing as forks arrive happens alongside the proofs, not after them. That
suite is the oracle every proof gets checked against, so it isn't a chore on the side,
it's the same work. Concretely: land the Heze (FOCIL) fork layer, absorb each spec alpha,
keep the suite green, account for every skipped vector explicitly so a coverage gap can't
hide as a silent pass.

## How the proofs get made

Tool-assisted, with the Lean kernel as the trust anchor. Statements and proofs both get
drafted with tool help, LLM-drafted candidates included.

Statements get the closer look, because a proof of the wrong statement is worth nothing
and the kernel won't catch that. So each one gets checked against the spec code it's
about, by review and by tool-assisted audit. The proofs lean on Lean's automation first,
`simp` and `omega` for the arithmetic and structural obligations, `bv_decide` for the
bit-level ones.

For verification it doesn't matter how a proof got generated, it needs to be correct.
Every proof is kernel-checked, the build is `sorry`-free, and each result carries a
`#print axioms` audit so the trust footprint is visible per theorem. Where something rests
on an added axiom we name it. The bitvector and narrow uint arms go through `bv_decide`,
which adds its own, and we say so. The wide 128 and 256 bit proofs close by induction
without `bv_decide` at all. Trust isn't uniform across these theorems, so it gets reported
per result and not as one blanket claim.

Assistance changes nothing about the guarantee. That's what the kernel is for.

## Roadmap

Cohort runs June to mid-November. Ordered so every stage lands as a useful upstream result
on its own.

| Month | Consensus layer |
|---|---|
| July | Heze fork layer, the merkle-branch proof, the shared verification roadmap |
| August | Structural and arithmetic invariants; cached-tree merkleization equivalence; conformance green as the spec moves |
| September | The shuffle is a real permutation, with its committee cluster. Greenfield, and the likely slip |
| October | Fork-choice store invariants; FOCIL inclusion-list validity on Heze; further merkleization proofs |
| November | Axiom audit across both layers, the documented pipeline, the final report. Doubles as schedule buffer |

Success criteria are in three tiers, minimum / target / stretch, so partial progress still
counts. If a target turns out intractable in the window, dropping it a tier is a
documented call and not a quiet disappearance.

## Where it stands

Snapshot as of the proposal presentation on 29 July 2026, check the
[dev updates](updates/index.md) for the current state.

None of this started in July, it started at onboarding, weeks before the proposal went in.
Merged: Gloas containers ([#5](https://github.com/etheorem/etheorem/pull/5)) and a build
fix ([#4](https://github.com/etheorem/etheorem/pull/4)). In review: the Heze fork layer
([#6](https://github.com/etheorem/etheorem/pull/6)), the fork-choice throw-faithfulness
sweep ([#22](https://github.com/etheorem/etheorem/pull/22)), and the verification roadmap
([#35](https://github.com/etheorem/etheorem/pull/35)) both lanes work from. Written but
not upstream yet: the merkle-branch completeness proof, `sorry`-free, going up next.

Raj's SSZ arms land on the same schedule and other contributors work their own pieces
alongside, so the repo moves faster than either lane does on its own.

## The cross-check, which is a side line

Separately and experimentally, I use etheorem to cross-check
[moonglass](https://github.com/brech1/moonglass), a Rust consensus client. Two halves to
it. Differential testing over shared and mutated inputs was the broad cheap one, thousands
of cross-checked cases and zero divergences, so that deep dive is wound down. The real
path is extraction, lifting a piece of the Rust client into Lean through Charon and Aeneas
and proving it computes what the spec says, each proof a checkable result whether or not
the whole client ever gets wired in. That only starts paying off once etheorem has the
protocol proofs to match against, so the order is proofs first and the cross-check rides
on top.

This does not prove a client correct and I'm not claiming it does. The fellowship proves
properties of the executable reference spec. The cross-check is me working out what
connecting a real client would take, which is a later research direction, not this six
months.

There's precedent for the shape of it. AWS's Cedar ships a Lean model with differential
testing against its Rust ([arXiv:2407.01688](https://arxiv.org/abs/2407.01688)), and the
EF's zkEVM Verification Project runs the same Charon+Aeneas→Lean pipeline
([arXiv:2605.30106](https://arxiv.org/abs/2605.30106)).

## Stack

Lean 4 (pinned v4.29.1) with Lake. consensus-spec-tests pinned per re-pin, currently
v1.7.0-alpha.11. The existing FFI SHA-256 / BLS / KZG shims. Rust (moonglass, `ssz_rs`)
with Charon and Aeneas for extraction. Python for the conformance and differential
drivers.

## Resources

- etheorem: <https://github.com/etheorem/etheorem>, start with `CONTRIBUTING.md`. Proof PRs
  are open, review welcome.
- The proposal: <https://github.com/eth-protocol-fellows/cohort-seven/pull/251>
- The proposal presentation: <https://www.youtube.com/watch?v=egjhzvLGlus&t=4743s> (EPF7
  Project Presentations 3, 29 July 2026, our segment starts at 1:19:03).
  [Slides](slides/etheorem-proposal-deck.pdf).
- Dev updates:
  <https://github.com/eth-protocol-fellows/cohort-seven/blob/main/development-updates.md>
- Me [@IvanAnishchuk](https://github.com/IvanAnishchuk) · Raj
  [@irajgill](https://github.com/irajgill) · Leo Lara
  [@leolara](https://github.com/leolara)
