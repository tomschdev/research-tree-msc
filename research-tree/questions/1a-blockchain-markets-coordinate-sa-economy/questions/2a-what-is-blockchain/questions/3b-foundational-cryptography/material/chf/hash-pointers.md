## Hash Pointers and the Block Chain

A **hash pointer** is a pointer to where some information is stored, together with a cryptographic hash of that information [@Narayanan2016Bitcoin]. An ordinary pointer only lets you retrieve the information. A hash pointer also lets you verify that it has not changed since the pointer was created. This relies on the collision resistance of the hash (see `chf.md`).

### A linked list with hash pointers

Take a linked list and replace each pointer with a hash pointer. Each block holds some data plus a hash pointer to the previous block. The hash in that pointer is computed over the *entire* previous block, including the previous block's own hash pointer. The result is a block chain: a tamper-evident log. We keep a hash pointer to the most recent block, the **head** of the list.

Tamper-evidence follows from hashing the whole block:

- Suppose an adversary modifies the data in some block $k$. The hash stored in block $k+1$ no longer matches block $k$, so the change is detected.
- To hide this, the adversary must also update the hash pointer in block $k+1$. But that pointer is part of block $k+1$'s contents, so block $k+1$'s hash changes too, and the pointer in block $k+2$ no longer matches.
- The mismatch moves forward one block at a time until it reaches the head. If we have kept the head hash pointer somewhere the adversary cannot alter, the tampering is detected.

So by remembering a single hash pointer, the one at the head, we can detect tampering anywhere in the list, all the way back to the first (genesis) block. Given the full list, anyone can check every link from genesis to the head and confirm the entire history against that one remembered value.

### Hash pointers in other data structures

Hash pointers work in any pointer-based data structure that has no cycles [@Narayanan2016Bitcoin]. Cycles are excluded because each node's hash depends on the nodes it points to. In a cycle, every node's hash would depend on itself, so no node's hash could be computed first. A *doubly* linked list with hash pointers in both directions is impossible for this reason. Block chains link backwards only.

The other important acyclic case is the binary tree with hash pointers, the **Merkle tree** (see `../merkle-trees/`).

### Towards consensus

A hash-pointer chain makes history tamper-evident, but only relative to a head that everyone agrees on. It does not say who may append the next block, or how a decentralised network agrees on a single head. Bitcoin's answer combines this structure with the search puzzles described in `chf.md`: the right to append a block is won by solving a proof-of-work puzzle. That mechanism belongs to the consensus question, not here.
