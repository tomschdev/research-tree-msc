## Merkle Trees

A **Merkle tree** is a binary tree built with hash pointers (see `../chf/hash-pointers.md`) [@Narayanan2016Bitcoin]. The construction is due to Ralph Merkle, who introduced hash trees to authenticate many values under a single hash [@Merkle1988Digital].

### Construction

- The **leaves** are the data items being committed to. Following Narayanan et al., these are called "data blocks". In Bitcoin they are the transactions of a single block (see *Merkle trees in Bitcoin* below).
- Each leaf is hashed. Adjacent hashes are then paired, and each pair is hashed together to form its parent: $H_{12} = H(H_1 \,\|\, H_2)$, and so on up the tree.
- This repeats until a single hash remains: the **Merkle root**.

Every node above the leaves is a hash pointer to its two children. The interior nodes are intermediate hashes and carry no data of their own. Only the leaves hold data.

```
                 H(1-8)                    root
              /          \
        H(1234)          H(5678)
        /     \          /     \
     H(12)   H(34)    H(56)   H(78)
     /  \    /  \     /  \    /  \
    H1  H2  H3  H4   H5  H6  H7  H8        leaf hashes
    |   |   |   |    |   |   |   |
    D1  D2  D3  D4   D5  D6  D7  D8        data blocks
```

**Size.** With $n$ leaves, the tree has depth $\lceil \log_2 n \rceil$ and about $2n - 1$ nodes. Doubling the number of data blocks adds one level to the tree.

**Tamper-evidence.** As with the block chain, remembering only the root is enough to detect tampering anywhere in the tree [@Narayanan2016Bitcoin]. Changing any data block changes its leaf hash. That changes the hash of its parent, and so on up to the root. To hide the change, an adversary would need a collision somewhere along the path.

**Acyclicity.** A Merkle tree is acyclic by construction, as any structure built from hash pointers must be. In a cycle, a node's hash would depend on itself, so it could never be computed.

### Proof of membership

The main advantage of the tree form is short proofs [@Narayanan2016Bitcoin]. To prove that a data block $D$ is in a tree with a known root, the prover supplies:

1. the data block $D$ itself;
2. the **sibling hash** at each level on the path from $D$ to the root. These are the hashes the verifier cannot compute alone.

The verifier hashes $D$ and combines the result with each sibling hash in turn, recomputing the path up to the root. They then compare the result with the root they already trust. The proof is valid if the two match.

*Example*: to prove $D_3$ is in the tree above, the prover supplies $D_3$, $H_4$, $H_{12}$ and $H_{5678}$. The verifier computes $H_3$, $H_{34}$, $H_{1234}$ and finally $H_{1\text{-}8}$, and compares it with the trusted root.

The proof contains one hash per level, so its size and the verification time are both $O(\log n)$. The verifier never needs the rest of the tree.

The proof is only as trustworthy as the root it is checked against. The verifier must get the root from a trusted source, such as a block header the network has agreed on.

### Proof of non-membership

A **sorted Merkle tree** orders its leaves by some total order, such as numerically by hash. It also supports proofs that an item is *not* in the tree, again in $O(\log n)$ [@Narayanan2016Bitcoin]:

- Find the position where the item would appear if it were present.
- Give membership proofs for the two leaves immediately before and after that position.
- Each proof also shows where its leaf sits in the tree, so the verifier can check that the two leaves are adjacent.
- If they are adjacent and the item would fall between them, the item is not in the tree.

This only works if the tree is sorted. In an unsorted tree, an item could appear at any position, and proving its absence would mean revealing every leaf.

### Merkle trees in Bitcoin

Bitcoin uses two hash-pointer structures together [@Narayanan2016Bitcoin]:

- **Across blocks**, a block chain: a linked list of blocks, each block header holding a hash pointer to the previous block.
- **Within each block**, a Merkle tree: its leaves are the block's transactions, and its root is stored in the block header.

Only the header takes part in the chain's hash pointers and in the proof-of-work puzzle (see `../chf/chf.md`). The root commits the header to every transaction in the block. The two structures sit at different levels. The leaves of a Merkle tree are not blocks of the chain, and the first leaf is not the genesis block.

This separation is what lets **lightweight clients** verify payments using block headers alone. Such clients are also called simplified payment verification (SPV) clients. To check that a transaction was included in a block, a client needs only that block's header and an $O(\log n)$ membership proof, not the block's full list of transactions [@Narayanan2016Bitcoin].
