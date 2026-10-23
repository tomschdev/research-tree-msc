## Digital Signatures

Together with cryptographic hash functions (see `../chf/chf.md`), digital signatures are the second foundational cryptographic building block of cryptocurrencies [@Narayanan2016Bitcoin]. A digital signature is the digital analogue of a handwritten signature, with two desired properties: only you can produce your signature, but anyone who sees it can verify that it is valid. Unlike a handwritten signature, a digital signature is tied to one particular document. It cannot be cut from one message and attached to another.

In a cryptocurrency, signatures authorise transactions. To transfer a coin, its owner creates a transaction ("pay this coin to address $A$") and signs it with their secret key. Any participant can then check, using only public information, that the transaction was authorised by the owner of the coin.

### The signature scheme

A digital signature scheme consists of three algorithms [@Narayanan2016Bitcoin]:

1. **Key generation**: $(sk, pk) \leftarrow \texttt{generateKeys}(keysize)$. A randomised algorithm that outputs a secret key $sk$, kept private and used to sign, and a public key $pk$, published so that anyone can verify.
2. **Signing**: $sig \leftarrow \texttt{sign}(sk, message)$. Produces a signature on $message$ under $sk$.
3. **Verification**: $\texttt{isValid}(pk, message, sig)$. Returns true if $sig$ is a valid signature on $message$ under the secret key corresponding to $pk$, and false otherwise. It uses only public information.

The scheme must satisfy two requirements:

- **Correctness**: valid signatures verify. For keys from $\texttt{generateKeys}$, $\texttt{isValid}(pk, m, \texttt{sign}(sk, m)) = \text{true}$ for every message $m$.
- **Unforgeability**: signatures are computationally infeasible to forge, as defined next.

### Existential unforgeability

The standard security notion is **existential unforgeability under adaptive chosen-message attack** [@Goldwasser1988Signature]. An adversary who knows $pk$ and has seen valid signatures on any number of messages of their own choosing should still be unable to produce a valid signature on any message they have not seen signed.

It is defined as a game between a challenger and an adversary [@Narayanan2016Bitcoin]:

1. The challenger runs $\texttt{generateKeys}$, keeps $sk$, and gives $pk$ to the adversary.
2. The adversary repeatedly chooses messages $m_1, m_2, \dots$ and receives $\texttt{sign}(sk, m_i)$ for each. The choices may be adaptive: each can depend on the signatures already received. The number of queries is limited only by the adversary's (polynomial) running time.
3. The adversary outputs a pair $(M, sig)$ for some message $M$ not among the queried $m_i$.
4. The adversary wins if $\texttt{isValid}(pk, M, sig)$ is true. Otherwise the challenger wins.

The scheme is unforgeable if every efficient adversary wins with only negligible probability. "Existential" means the adversary wins by forging a signature on *any* new message, even a meaningless one. The definition does not require that a message have only one valid signature; ECDSA signing is randomised, so the same message can have many valid signatures.

### Signatures in practice

**Signing a hash.** Signature algorithms take inputs of limited size. In practice one signs $H(m)$, the hash of the message, rather than $m$ itself. Because $H$ is collision resistant, a signature on $H(m)$ is as good as a signature on $m$: finding a second message with the same hash, so as to reuse the signature, would require a collision [@Narayanan2016Bitcoin].

A related technique is to sign a hash pointer. Signing the head hash pointer of a block chain or the root of a Merkle tree covers the entire structure it points to (see `../chf/hash-pointers.md`).

**Bitcoin's scheme.** Bitcoin uses the Elliptic Curve Digital Signature Algorithm (ECDSA) [@Johnson2001ECDSA] over the elliptic curve secp256k1. The key and signature sizes are [@Narayanan2016Bitcoin]:

| | Size |
|---|---|
| Secret key | 256 bits |
| Public key | 512 bits uncompressed, 257 bits compressed |
| Message signed (a hash) | 256 bits |
| Signature | 512 bits |

Since the Taproot upgrade (2021), Bitcoin also supports Schnorr signatures over the same curve.

**Security level.** secp256k1 provides roughly 128 bits of security: the best known attacks on the underlying elliptic-curve discrete-logarithm problem need on the order of $2^{128}$ operations [@Narayanan2016Bitcoin]. Like collision resistance for hash functions, this rests on the absence of known attacks, not on a proof.

**Dependence on randomness.** ECDSA needs good randomness twice. It needs it in $\texttt{generateKeys}$, so that $sk$ is unpredictable. It also needs it in every call to $\texttt{sign}$, which draws a fresh secret per-signature nonce. If that nonce is ever reused for two different messages, or is predictable, anyone can compute $sk$ from the signatures alone. Even small biases in nonce generation have been exploited to recover secret keys from signatures published on real cryptocurrency blockchains [@Breitner2019Biased]. A weak random source therefore compromises the key even when the algorithm itself is sound.

### Public keys as identities

A public key can serve as an identity [@Narayanan2016Bitcoin]. If $\texttt{isValid}(pk, m, sig)$ holds, then whoever holds the matching $sk$ has, in effect, said $m$. So "speaking as" $pk$ means signing with its secret key.

This enables **decentralised identity management**:

- **Traditional systems**: a user registers an identity with a central authority, which issues and records it.
- **Signature-based systems**: anyone can create a new identity at any time by running $\texttt{generateKeys}$. No registration is needed. The key space is large enough that two people will not, in practice, generate the same key.

In Bitcoin these identities are **addresses**. An address is not the public key itself but is derived from a hash of it. In the classic address format, the address encodes $\text{RIPEMD-160}(\text{SHA-256}(pk))$. To spend coins sent to an address, the owner reveals $pk$ along with a signature. Verifiers check both that $pk$ hashes to the address and that the signature is valid under $pk$.

Such identities are cheap, unlimited and not linked to a real-world identity by default. Users can create as many as they like. This makes Bitcoin pseudonymous, not anonymous: activity under one address can still be linked and analysed.
