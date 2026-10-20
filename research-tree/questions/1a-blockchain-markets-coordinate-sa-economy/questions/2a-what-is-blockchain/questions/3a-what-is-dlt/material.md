# What is DLT?

When breaking blockchain down to core components, one should actually be studying DLT systems.
Blockchain systems are commonly considered a subset of Distributed Ledger Technology, a broader definition that encompasses the significant variations seen in the core design of blockchain systems.

A DLT is formally defined as a system of electronic records that:
- enables a network of independent participants to establish authoritative ordering of cryptographically validated transactions.
- ensures persistence by replicating data across mulitple nodes
- maintains tamper-evidence by linking records with cryptographic hashes
- generates an authoritative shared state - the ledger - which emergences without reliance on a trusted central party.

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

### Communications Component
- Network access: governs participant entry to the network, establishing whether the network is open (permissionless) or closed (permissioned).
- Data broadcast: defines the mechanisms used to transmit and relay messages, transactions, and blocks across connected nodes, determining whether data visibility is public or private.
- Transaction initiation: Specifies the rules and authorisation requirements for participants to generate, cryptographically sign, and broadcast new transaction proposals to the network.
### Transaction Processing Component
- Record proposal: The process wherein designated record producers select unconfirmed transactions from their local logs (mempools) and bundle them into candidate records (e.g., candidate blocks) for network distribution.
- Conflict resolution rule: The consensus algorithm and tie-breaking logic used by network participants to agree upon a single authoritative set of records when presented with conflicting updates or competing subchains.
- Incentivised transaction: processing: The structurual mechanism that encourages record producers the expend computational or economic resoruces to validate transactions and propose candidate records. This operates along a clear securituy specturem.
  - intrinsinc economic intecentive models: essential for open, permissionless systems (e.g., Bitcoin or Ethereum), where record producers are compensated via native token rewards and transaction fees to ensure non-strategic, honest participation in adversarial environments.
  - access control & contractual models: typical for closed permissioned systems (e.g., enterprise consortia) where record producers are bound by legal contracts, regulatory oversight, and administrative access controls, rendering intrinsic financial token rewards unnecesasry.

### Validation Component
- Transaction validation: the independent verifications procedures carried out by auditing nodes to confirm that submitted transactions compley with protocol rules priror to execution and inclusion in a log.
- Record validation: The process by which auditing nodes verify candidate records submitted by record producers beofre appending them to their journal instnaces.
- Transaction finality: The operational state transition spanning provisional settlement to permanent settlement, determining the degree of difficulty or impossibility associated with reversing confirmed records:
  - Probabilistic Finality: found in nakamoto-style consensus mechanisms, where settlement is initially provisional and transaction finality increases asymptotically over time as additional blocks are built on top (reducing the probability of reversal near to zero)
  - Deterministic Finality: found in pbft-style or voting-based consensus variants, where a candidate reocrd achieves immediate, irreversible permanent settlement as sson asa required supermajoirty threshold of signatures is secured.


## The Data Layer
The Data Layer is the authoritative, shared information strcuture-the ledger- that results from continuous execution of protocol rules by the network layer.

### Taxonomic Progression of Ledger Data
- Unconfirmed transactions: Raw, cryptographically signed proposals created by end users to request a state transition (e.g., an asset transfer or contract invocation), awaiting confirmation
- Log (mempool): An unordered collection of valud, unconfirmed transactions recieved and maintained locally by an individual node prior to formal incorporation into a record.
- Record: A structred bundle of transaction sleected from a log by a recird porducer (forming a candidate record) and subjected to network consensus rules.
- Journal:  An indidvudal node's local, partial, and provisional instance of processed records. Hournals are heterogeneous across nodes and represent local state copes prior to full system convergence.
- Ledger: The emergent, globally synchronised, and authoritative set of records collectively held in common by a substantial majoirty of network participants, representing final state alignment.
