---
date: 2026-11-04
title: "EPF Cohort 7 Final Report - Ivan Anishchuk"
description: "Ivan Anishchuk's EPF cohort-seven final report: machine-checked proofs about the Ethereum consensus protocol on the executable Lean 4 spec model in etheorem, from throw-faithfulness and invariants to FOCIL + ePBS finality and Casper FFG accountable safety, and the first steps toward a client."
categories:
  - project-update
tags:
  - epf
  - lean4
  - formal-verification
  - focil
  - epbs
  - casper-ffg
  - libp2p
  - shadow-node
---

# EPF Cohort 7 Final Report - Ivan Anishchuk

Short version:

- Project: machine-checked proofs about the Ethereum consensus protocol, done on the executable
  Lean 4 spec model in [etheorem](https://github.com/etheorem/etheorem).
- Done: the Heze (FOCIL) fork layer, the verification roadmap, a model that raises where the
  pyspec raises (guided by the proof work), arithmetic and structural invariants, Merkle-branch
  completeness, the shuffle and committee partition, FOCIL + ePBS from one node to finality, and
  Casper FFG accountable safety.
- Eight of my etheorem PRs are merged; the proof stack (#103–#115, #134–#140) is open for review.
- In the last weeks I started on running the model as a client: libp2p in Lean 4
  ([leanp2p](https://github.com/etheorem/leanp2p), five PRs merged) and a shadow node that follows
  a devnet through the etheorem model.

## The project

etheorem is an executable Lean 4 model of the consensus spec (Fulu, Gloas, Heze) that passes the
official consensus-spec-tests vectors. My part, per the
[proposal](https://github.com/eth-protocol-fellows/cohort-seven/blob/main/projects/etheorem-consensus-proofs-lean4.md),
was proving some cool properties of the protocol on this model and keeping the model faithful to the pyspec.

Every proof PR lists the axioms it rests on. CI collects them and fails on any outside the
allow-list, so the trust footprint is checked, not claimed. The weekly details are in the
[dev updates](https://ivananishchuk.github.io/eth-protocol-fellowship/).

## What I did in etheorem

**Spec pin and Heze.** Re-pinned the model to consensus-specs `v1.7.0-alpha.11` with the Gloas
EIP-8282 builder containers ([#5](https://github.com/etheorem/etheorem/pull/5), merged) and wrote
the Heze fork layer with EIP-7805 FOCIL
([#22](https://github.com/etheorem/etheorem/pull/22), merged). All of my proofs are on this pin.
Michael Sproul later re-pinned main to `v1.7.0-beta.4`
([#147](https://github.com/etheorem/etheorem/pull/147)).

**Throw-faithfulness.** The model used to wrap around or return a default where the pyspec
raises: missing keys, failed asserts, `uint64` overflows, out-of-range reads. A proof about such a
model says nothing about the spec, so this came first.
- Fork choice, including `get_forkchoice_store` and FOCIL:
  [#22](https://github.com/etheorem/etheorem/pull/22) (merged).
- An append to a full SSZ list raises: [#120](https://github.com/etheorem/etheorem/pull/120)
  (merged).
- Seven spec functions reject on overflow, each with a proof of where the reject can't fire:
  `compute_start_slot_at_epoch` ([#103](https://github.com/etheorem/etheorem/pull/103)),
  `compute_activation_exit_epoch` ([#104](https://github.com/etheorem/etheorem/pull/104)), the
  exit and consolidation churn ([#105](https://github.com/etheorem/etheorem/pull/105)),
  `process_deposit`'s index ([#106](https://github.com/etheorem/etheorem/pull/106)), and the
  Gloas builder pending-balance sums ([#110](https://github.com/etheorem/etheorem/pull/110)).
  For example, an epoch that came out of `compute_epoch_at_slot` never overflows
  `compute_start_slot_at_epoch`, with no extra hypothesis.
- The rest of fork choice, the shuffle and committees, epoch processing and block operations,
  each area with pin tests that replay the pyspec outcome. It also removes the eth1 deposit path
  Fulu dropped and adds the EIP-7892 blob schedule:
  [#134](https://github.com/etheorem/etheorem/pull/134).

This matters outside the repo too. The Lighthouse team has started using etheorem to verify
Lighthouse: Eitan Seri-Levi
[describes](https://unclebill.blog/posts/etheorem-and-a-small-spec-inconsistency) an equivalence
proof of their Gloas epoch processing against the model, one of its 17 steps at a time. Where
the model didn't raise and the spec did, their theorems needed preconditions to rule those
states out. Eitan's own fixes in the same direction
([#146](https://github.com/etheorem/etheorem/pull/146),
[#151](https://github.com/etheorem/etheorem/pull/151), plus overflows and out-of-bounds reads in
epoch processing) let them drop two of those preconditions and prove a stronger statement: on
any state, Lighthouse and etheorem reach equal states or both fail.

Found along the way: the Gloas consolidation churn limit has no `MIN` floor, so it can be zero
(the old model divided by it and got `0`), and the zero-hash table had drifted from pyspec
([#40](https://github.com/etheorem/etheorem/issues/40)).

**Roadmap.** Twenty proof targets in four tiers (Merkleization, shuffle and committees, state
invariants, fork choice + FFG), each tied to a spec function, added as rows of etheorem's proof
ledger ([#35](https://github.com/etheorem/etheorem/pull/35), merged). Each row cites the lines of
the fork body it's about, and CI fails when a citation stops matching. I also fixed the axiom
allow-list, which named the two SHA-256 FFI axioms under the wrong namespace
([#79](https://github.com/etheorem/etheorem/pull/79), merged).

**Invariants.**
- The Fulu balance mutators never wrap: seven theorems, including the overflow reject and the
  exact stored sum ([#80](https://github.com/etheorem/etheorem/pull/80), merged). Both mutators
  had to become rejecting `StateTransition` actions first, with checked reads and adds. The PR
  also maps each reference-test runner to the exceptions its wrapper catches, so a reject is
  scored as faithful only where the pyspec test expects one.
- Slot/epoch round trip and monotonicity at Fulu, Gloas and Heze
  ([#103](https://github.com/etheorem/etheorem/pull/103)).
- The deposit path keeps `validators` and `balances` the same length
  ([#107](https://github.com/etheorem/etheorem/pull/107)).
- Gloas `apply_withdrawals` never raises a builder balance, over any withdrawals array
  ([#108](https://github.com/etheorem/etheorem/pull/108)).
- At mainnet, an active count in `[32, 2^22]` puts every committee size in `(0, 2048]`, the
  bound the Dafny work proves as `ActiveValidatorBounds`
  ([#109](https://github.com/etheorem/etheorem/pull/109)).

**Merkleization.** `compute_merkle_branch_root` with the spec's length guard
([#71](https://github.com/etheorem/etheorem/pull/71), merged). My first completeness stack
([#42](https://github.com/etheorem/etheorem/pull/42),
[#66](https://github.com/etheorem/etheorem/pull/66),
[#67](https://github.com/etheorem/etheorem/pull/67),
[#72](https://github.com/etheorem/etheorem/pull/72)) was stated over the cached tree. Leo's
[#100](https://github.com/etheorem/etheorem/pull/100) moved proofs to the pure path, building on
#71's branch module, so I closed it. What it still adds is open:
- `is_valid_merkle_branch` accepts the opening `merkleize` builds, for any chunk list, depth and
  index ([#111](https://github.com/etheorem/etheorem/pull/111)).
- A branch into a container field verifies against the container's `hash_tree_root` at one to
  three levels of nesting, applied at Fulu's `finalized_checkpoint.root` (gindex 169) and the
  Gloas execution block hash (gindex 832)
  ([#112](https://github.com/etheorem/etheorem/pull/112)). The proofs use one axiom, that the FFI
  SHA-256 combine matches the spec; with the pure-Lean hasher they use none.

**FOCIL + ePBS.** A builder whose payload leaves out a transaction of an honest inclusion list
loses the payload and still pays its bid on quorum. This is the intended design (Zanolini and
Saltini note its properties haven't been proven formally); Rahul Barman's
[Formalizing FOCIL in Lean 4](https://ethresear.ch/t/formalizing-focil-in-lean-4/24950) proves
the network-level claim on an abstract model. Mine is on the executable Heze spec functions and
includes ePBS.
- One node, one block: what a failed inclusion list costs, the fork-choice map laws, and the
  inclusion dichotomy ([#113](https://github.com/etheorem/etheorem/pull/113)–[#115](https://github.com/etheorem/etheorem/pull/115)).
- Every honest node in the next slot, including one that never got the payload; honest
  attesters don't vote for it and honest proposers build without it
  ([#135](https://github.com/etheorem/etheorem/pull/135)).
- The slots after, as a weight race between the FULL and EMPTY branches: more than 70% honest
  balance in the first committee keeps EMPTY ahead
  ([#136](https://github.com/etheorem/etheorem/pull/136),
  [#138](https://github.com/etheorem/etheorem/pull/138)).
- Finality: if the honest votes are included in time, every honest node finalizes on the EMPTY
  side within four epochs, and after that a head with the payload needs slashing evidence
  ([#140](https://github.com/etheorem/etheorem/pull/140)).

The assumptions are hypotheses the theorems take: a lawful EL, one list per validator, timely
first arrival, honest committees, and a few about the store. Each level has a minimal-preset test
witness that meets all of them at once; the finality one finalizes epoch 4 at slot 64.

**Shuffle and committees.** `compute_shuffled_permutation` is a permutation for any seed and
hash, and each active validator sits in exactly one committee of an epoch
([#137](https://github.com/etheorem/etheorem/pull/137)). The payload race uses it to count each
vote once.

**Casper FFG.** An abstract FFG model where each side of a fork keeps its own stake, a proof that
the spec's justification and finalization refine it, and accountable safety for two honest Heze
fork-choice stores: the validators that signed slashable pairs hold at least a third of the stake,
minus a term for how far the stake moved after the fork. The PR bounds that drift, and a test
checks that `process_attester_slashing` accepts the evidence
([#139](https://github.com/etheorem/etheorem/pull/139)).

## Toward a client

The future-work list in my last report started with libp2p in Lean and a client spike. Both are
underway.

**leanp2p.** [leanp2p](https://github.com/etheorem/leanp2p) is a libp2p stack in Lean 4 (an
Invisible Garden project), aimed first at the consensus layer: tcp + noise + yamux, identify,
req/resp and gossipsub v1.1. It binds mature C libraries through small shims behind Lean
interfaces, and is built bottom-up with several contributors, against Leo's spike branch as the
reference. My merged parts:
- W1.1, the concurrency primitives ([#27](https://github.com/etheorem/leanp2p/pull/27), and
  [#38](https://github.com/etheorem/leanp2p/pull/38)).
- W2.1, the unsigned varint codec and its laws
  ([#34](https://github.com/etheorem/leanp2p/pull/34)).
- W4.1, the connection layer and a simulated transport
  ([#32](https://github.com/etheorem/leanp2p/pull/32)).
- W3.2, the OpenSSL 3 shim and the pins to etheorem's crypto packages
  ([#39](https://github.com/etheorem/leanp2p/pull/39)).

Open: the Crypto facade with an RNG seam and a cross-check against the backends
([#41](https://github.com/etheorem/leanp2p/pull/41)), and the ENR codec
([#43](https://github.com/etheorem/leanp2p/pull/43)).

**Shadow node.** etheorem-shadow-node runs a node through the
etheorem Fulu model and compares it with a real client, block by block. Every block goes through
the model with real BLS and KZG checks, and `state_transition` asserts the `state_root`, so
agreement means the same state.
- It keeps one fork-choice store from genesis or a checkpoint and feeds it the blocks, data
  columns and gossip votes, then compares the head and checkpoints with the host (Lighthouse).
- It drives its own Geth over the Engine API (`newPayload`, `forkchoiceUpdated`, with the JWT
  and HMAC in Lean), so the execution side follows the model's fork choice.
- It serves a read-only Beacon API from its own store, enough for Lighthouse to checkpoint-sync
  from it, and `api-diff` compares every endpoint with the host.
- `shadow_node` joins the p2p network as one Lean process. A Rust library over Lighthouse's
  network crate only moves bytes; the event loop, sync, column assembly and gossip validation
  are in Lean. This is the stand-in until leanp2p can carry it.
- It runs on Kurtosis devnets, including a three-node one (two Lighthouse, one Grandine, 1056
  validators) with slashings, exits and deposits in the blocks.

It's not a client yet: it serves no blocks or columns to peers and doesn't rebuild columns from
half of them. Running on a real network also showed where the spec shape costs too much:
an epoch-boundary proposer check ran an epoch transition per column message (100 s for one
slot, 7 s after caching it per parent), and the pyspec store never prunes, so the node prunes to
the finalized checkpoint and differs from the spec in two documented cases.

## What I learned

- Formal verification of the spec matters, but most client bugs show up elsewhere: networking
  and caching, the parts that are beyond the spec and hard to verify. A common
  one is a client caching values from gossip before validation and letting that cache feed into its logic. Doing something about those parts is hard but is important direction of work.
- As the spec is optimized for expressiveness and Lean model is optimized for
  proofs some things are being quite slow to be used as is in a real node (regardless of which
  language they are implemented in) but Lean has convenient `implemented_by` pattern using which we
  can provide optimized implementations of some functions and formally prove that they are
  equivalent to the spec.

## Future work

- Get the open proof PRs merged, and publish the ethresear.ch posts (FOCIL + ePBS parts 1–3, the
  shuffle, FFG).
- Re-pin my proofs to the current spec release and keep the model current.
- leanp2p: finish the crypto facade and ENR, then the rest of the consensus-layer stack, and move
  the shadow node from the Rust library to it.
- Turn the shadow node into an experimental client: serve blocks and columns to peers, rebuild
  columns, add a database layer, and attach `implemented_by` versions where the spec shape is too
  slow, each proved equal to the spec.
- Prove existing client code equivalent to the Lean model by extracting it into Lean (Lighthouse
  has started on its epoch processing), and generate new test vectors from the model.
- Formalize the conversion from the Python spec to our Lean dialect. It's mostly LLM-assisted
  now; deterministic tooling could take over a good part of it.
- More proofs: light-client sync completeness, fork-choice safety and liveness, sync committees,
  PeerDAS, and the FOCIL + ePBS and FFG assumptions as theorems.

## EPF experience

I was not the only contributor joining etheorem in these months and I would contribute
regardless but comparing myself to others the program really provided me with good structure for getting some
things done and published (even if some are still arguably 95%) - there's a good chance I'd
work on some of them for much longer if I didn't have to write reports and talk
on standups about what I've done (at minimum it prompted me to publish everything as soon as not embarrassing
and to review and finish some things that would otherwise simmer much longer).

The learning part was also extremely helpful, having people from various corners of
the protocol come and talk about their work is extremely important to aspiring core
devs.

## Resources

- etheorem: https://github.com/etheorem/etheorem
- leanp2p: https://github.com/etheorem/leanp2p
- Proposal: https://github.com/eth-protocol-fellows/cohort-seven/blob/main/projects/etheorem-consensus-proofs-lean4.md
- Dev updates: https://ivananishchuk.github.io/eth-protocol-fellowship/
- My etheorem PRs: https://github.com/etheorem/etheorem/pulls/IvanAnishchuk
- My leanp2p PRs: https://github.com/etheorem/leanp2p/pulls/IvanAnishchuk
- Lighthouse verifying against etheorem (Eitan Seri-Levi): https://unclebill.blog/posts/etheorem-and-a-small-spec-inconsistency
- etheorem update on ethresear.ch: https://ethresear.ch/t/etheorem-update-the-complete-executable-consensus-specs-written-in-lean-4/26063
- EPF Day talk at Devcon 8, with Raj Gill: https://app.devcon.org/schedule/etheorem-lean-4-consensus-spec-proofs
