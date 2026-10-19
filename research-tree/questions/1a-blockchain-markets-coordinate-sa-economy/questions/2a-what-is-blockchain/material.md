## What is Blockchain?

Blockchain is one the most notorious technology buzzwords of the early 21st century.  


The term blockchain has no standard technical definition but is a loose umbrella term used by various parties to refer to systems that bear varying levels of resemblance to bitcoin and its ledger [@Narayanan2017Pedigree].

With that being said, another explanation of blockchain is supplied:

> Blockchain is an emerging technology for decentralized and transactional data
> sharing across a large network of untrusted participants. It enables new forms
> of distributed software architectures, where components can find agreements on
> their shared states without trusting a central integration point or any
> particular participating components [@Xu2016Connector, p. 182].

Blockchain refers to a database architecture with a minimal set of properties; however blockchain systems can be built with various differing configurations beyond the minimal set of properties. [@Xu2017Taxonomy] contribute a taxonomy of the various blockchain variants.

It should be emphasised that blockchain is system architecture and not an
end-user application, as is sometimes a common misconception. Therefore, it is
appropriate that end users of a blockchain based application are unaware of the
fact that they are interacting with blockchain. Any scenario that requires the
accumulation and storage of state across multiple nodes is a candidate for
adopting a blockchain-based software architecture. Blockchain has attracted a
lot of attention as an emergent technology and is occasionally misused for
various reasons. [@Wust2018Need] provides a decision tree that assists
speculators in assessing whether a blockchain architecture is applicable for a
specific system.

The concept of blockchain was popularised by the first major application that
developed/utilised its foundational properties: Bitcoin. [@Nakamoto2008Bitcoin]
introduces Bitcoin as a system for electronic transactions without relying on
trust. The work builds on the existing concept of coins as a chain of digital
signatures and introduces a novel solution to prevent double-spending by way of
a peer-to-peer network with a proof-of-work consensus algorithm which makes it computationally infeasible for an
attacker to capture the network and its distributed state.

[@Narayanan2017Pedigree] explains that bitcoin was founded on approximately 3
decades of research into cryptography and its applications to digital cash,
providing explanations and references to the concepts that comprise and predate
bitcoin.

## What is the minimal set of properties of a blockchain architecture?

When breaking blockchain down to core components, one should actually be studying DLT systems.
Blockchain systems are commonly considered a subset of Distributed Ledger Technology, a broader definition that encompasses the significant variations seen in the core design of blockchain systems.
[@Rauchs2018DLT] compiles a comprehensive overview of DLT, yielded the following learnings:

A DLT is formally defined as a system of electronic records that:
- enables a network of independent participants to establish authoritative ordering of cryptographically validated transactions.
- ensures persistence by replicating data across mulitple nodes
- maintains tamper-evidence by linking records with cryptographic hashes
- generates a shared state - the ledger - which is an authoritative version which does not rely on a trusted central party.

"A Distributed Ledger Technology (DLT) system is fundamentally a multi-party 'consensus machine'—a system of electronic records designed to enable a network of independent participants to establish consensus around the authoritative ordering of cryptographically-validated ('signed') transactions in an adversarial environment, without relying on a central coordinator." [@Rauchs2018DLT]

Key criteria and necessary conditions are as follows:
- shared recordkeeping: enables multiple separate entities to collectively create, maintain and update an authoritative set of shared records.
- multi-party consensus: enables agreement on shared records without a central authority, either permissionlessly (without prior trust), or permissioned (preapproved record producers)
- independent validation: allows each fully validating participant (auditor/validtor) to independently verify transaction states and system integrity from genesis.
- tamper-evidence: enables participants to trivially detect any non-consensual modifications to past records using cryptogrpahic linkages
- tamper-resistance: makes it structurally infeaisbale for a single party to unilaterally alter previous transascitons 

Three layers comprise all DLT systems: Protocol Layer, Network Layer, Data Layer.

Protocol Layer: The foundational, software-defined ruleset that codifies the system's constitutional design, governance mechanisms, and initial operational parameters.
Network Layer: The operational environment consisting of interconnected, heterogeneous actors and processes that implement protocol rules to communicate, process transactions, reach consensus, and maintain system state.
Data Layer: The emergent, shared information structure—the ledger—resulting from network execution, which stores persistent, tamper-evident, time-ordered transaction data synchronised across participants.

The protocol layer is designed by developers of the blockchain-system with intent for the resulting protocol to be run by a network of participants, comprising the network layer, in order to support the decentralised accumulation of the contents in accordance with the design of the protocol layer, to result in the maintenance of the data layer.


## Protocol Layer
The foundational, constitutional ruleset of a DLT system, that codifies how a system is initialises, how rules are defined and how the system evolves over time.

Components of the protocol layer are either genesis components or alteration components. The genesis components, which apply static unchanging rules from the initiation of the system, are: inter-system dependencies, codebase creation and rule initiation. The alteration components, which are mechanisms for adapting dynamic properties of the system (which may in themselves be mechanisms) are protocol governance and protocol change.

### Inter-system Dependencies
Defines the operational boundaries of the system, specifying whether the DLT system is self-sufficient or dependent upon external systems to function properly.

### Codebase Creation 
The development of foundational software rulesets which are either constructed from scratch or adapted.

### Rule Initiation
Establishes the initial ruleset, parameters, and first record upon which the system operates at launch.

### Protocol Governance
The set of decision-making processes (often conducted off-chain) that determines how rules are evaluated, negotiated, and modified by system actors.

### Procotol Change
The formal mechanism utilised to implement agreed-upon modifications to the underlying software ruleset across the system.


## Network Layer
The practical implementation and exectution of protocol rules by interconnected participants. Structured into three components:

