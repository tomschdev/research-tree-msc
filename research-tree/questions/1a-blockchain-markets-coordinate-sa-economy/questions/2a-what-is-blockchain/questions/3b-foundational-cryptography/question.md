---
id: 3b-foundational-cryptography
path: 1a2a3b
question: "What is the foundational cryptography of blockchain?"
parent: 2a-what-is-blockchain
candidate-conclusions: [converged, contested]
candidate-conclusion-definitions-path: ./workflow/candidate-conclusion-definitions.yaml
opened: 2026-10-20T13:18:01Z
updated: 2026-10-20T13:18:01Z
---

## Rationale


2a's properties of blockchain rest on cryptographic mechanisms. Tamper-evidence comes from linking
records with hashes. Transaction authorisation comes from digital signatures. Agreement in an
adversarial setting comes from consensus with Byzantine fault tolerance. 2a needs to name these
building blocks and the property each one secures. Then the definition can say which part of
"shared trust" is cryptographic and which is institutional or economic.

What each candidate conclusion means here:

- **converged**: systematic accounts of blockchain cryptography (at least Raikwar et al. 2019,
  Zhang et al. 2019 and Narayanan et al. 2016) agree on a core set of building blocks:
  cryptographic hash functions, digital signatures, and a consensus mechanism tolerant of
  Byzantine faults. They also agree on the property each one secures. That mapping is adopted.
- **contested**: these sources materially disagree. They may disagree on which building blocks
  are foundational rather than optional (e.g. zero-knowledge proofs, Merkle structures). Or they
  may disagree on whether consensus is a cryptographic building block at all or a
  distributed-systems one. The Finding names the competing accounts and states which is adopted
  and why.
