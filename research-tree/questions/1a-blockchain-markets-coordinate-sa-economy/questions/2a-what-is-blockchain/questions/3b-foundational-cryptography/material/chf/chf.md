## Cryptographic Hash Functions

Cryptocurrencies have no intermediary to resolve disputes, so the integrity of the currency must be enforced by cryptography alone. Two primitives carry most of that weight: cryptographic hash functions (CHFs), covered here, and digital signatures (see `../digital-signatures/`) [@Narayanan2016Bitcoin].

A hash function maps an input string of arbitrary size to a fixed-size output (256 bits in the case of SHA-256), and is efficiently computable: hashing an $n$-bit input takes $O(n)$ time [@Narayanan2016Bitcoin]. CHFs underpin data integrity and tamper-evidence (see `hash-pointers.md`), and supply the search puzzles used for proof-of-work consensus.

A hash function is called cryptographic when it additionally satisfies the security properties below. Collision resistance and hiding are security properties in the usual sense; puzzle-friendliness is a property Narayanan et al. introduce specifically because proof-of-work needs it, and is not a standard requirement of a CHF.

### Collision Resistance

A hash function $H$ is collision resistant if it is computationally infeasible to find two distinct inputs $x \neq y$ such that $H(x) = H(y)$.

Collisions must exist: the input space is infinite and the output space is finite, so by the pigeonhole principle many inputs share each output. The claim is only that nobody can *find* one.

- **Pigeonhole principle**: if there are more inputs than outputs, at least one output is shared by two or more inputs.
- **Birthday paradox**: finding *some* collision takes far fewer random tries than intuition suggests. With 365 possible birthdays, 23 people give a >50% chance that two share a birthday, because every pair is a candidate match and the number of pairs grows quadratically with group size. In general, a collision is expected after roughly the square root of the output-space size. For a 256-bit hash that is about $2^{128}$ random inputs.

This generic attack works against every hash function, but it is infeasible in practice: Narayanan et al. estimate that a computer computing 10,000 hashes per second would need more than $10^{27}$ years to perform $2^{128}$ hashes [@Narayanan2016Bitcoin]. Collision resistance for a particular function is therefore a belief backed by failed cryptanalysis, not a proof. Functions once believed collision resistant (e.g. MD5) have since been broken.

#### Application: message digests

Collision resistance lets a short hash stand in for a large file. Compute $H(f)$ for a file $f$ and keep it locally; upload $f$ to untrusted storage. When downloading the file $F$ later, recompute $H(F)$. If $H(F) = H(f)$, then $F = f$, since otherwise the storage provider would have produced a collision. This requires that the reference hash be kept somewhere the adversary cannot alter.

### Hiding

Hiding captures the intuition that a hash is one-way: from $y = H(x)$ alone, you cannot work out $x$.

This fails when $x$ comes from a small or predictable set. If $x$ is either `"heads"` or `"tails"`, an observer can hash both candidates and see which one matches $y$. Hiding therefore requires an input with high **min-entropy**: a distribution so spread out that no single value has more than a negligible probability. (Formally, min-entropy is $-\log_2 \max_x \Pr[X = x]$. A uniformly random 256-bit string has min-entropy 256.)

Formally, $H$ is hiding if, when a secret value $r$ is chosen from a distribution with high min-entropy, then given $H(r \,\|\, x)$ it is infeasible to find $x$ [@Narayanan2016Bitcoin]. Concatenating the random $r$ supplies the min-entropy that $x$ may lack, so hiding holds even when $x$ itself is predictable.

#### Application: commitment schemes

A commitment is the digital analogue of sealing a message in an envelope and handing it over: the recipient cannot read it yet (hiding), and the sender cannot change it afterwards (binding).

- **Commit**: choose a random 256-bit nonce, publish $com = H(nonce \,\|\, msg)$, keep $nonce$ and $msg$ secret.
- **Reveal**: publish $nonce$ and $msg$; anyone can check that $H(nonce \,\|\, msg) = com$.

The two security properties of the scheme follow directly from the two properties of $H$:

- **Hiding**: given $com$, it is infeasible to find $msg$. This is the hiding property of $H$, with $nonce$ as the high min-entropy value $r$. Without the nonce, a message drawn from a small set (e.g. `"I love you"` / `"I hate you"`) could be recovered by guessing.
- **Binding**: it is infeasible to find $(nonce', msg') \neq (nonce, msg)$ with $H(nonce' \,\|\, msg') = com$. Such a pair would be a collision, so binding follows from collision resistance.

### Puzzle-Friendliness

$H$ is puzzle-friendly if, for every possible $n$-bit output value $y$, when $k$ is chosen from a distribution with high min-entropy, it is infeasible to find $x$ such that $H(k \,\|\, x) = y$ in time significantly less than $2^n$ [@Narayanan2016Bitcoin].

Informally: if part of the input is randomised, there is no shortcut to steering the output toward a chosen value. Trying random $x$ is essentially the best available strategy.

#### Application: search puzzles and proof-of-work

A search puzzle consists of:

- a hash function $H$;
- a puzzle-ID $id$, chosen from a high min-entropy distribution;
- a target set $Y \subseteq \{0, 1\}^n$.

A solution is any $x$ such that $H(id \,\|\, x) \in Y$. Puzzle-friendliness implies that no solving strategy is much better than trying random values of $x$. The random $id$ ensures that solutions cannot be precomputed.

The size of $Y$ sets the difficulty. If $Y$ is the whole output space, every $x$ is a solution. If $Y$ contains a single value, solving takes about $2^n$ attempts. In general the expected number of attempts is $2^n / |Y|$, so shrinking $Y$ makes the puzzle proportionally harder.

In practice $Y$ is defined by a numerical threshold, $H(id \,\|\, x) \leq T$. Bitcoin mining is a search puzzle of this form: miners vary a nonce in the block header until the block's hash is at or below the current target. Bitcoin applies SHA-256 twice (SHA-256d) to the header.

### SHA-256 and the Merkle–Damgård Construction

SHA-256 produces a 256-bit output, i.e. a value in $[0, 2^{256} - 1]$, and accepts inputs of any length. It achieves this with the **Merkle–Damgård construction**, which turns a fixed-input-length compression function into a hash function for arbitrary-length inputs [@Merkle1990Certified; @Damgard1990Design].

SHA-256's compression function $C$ takes a 768-bit input and produces a 256-bit output [@Narayanan2016Bitcoin]. To hash a message $M$:

1. **Pad** $M$ so its length is a multiple of 512 bits. The padding ends with a 64-bit field encoding the original length of $M$.
2. **Split** the padded message into 512-bit blocks $b_1, \dots, b_L$.
3. **Chain**: set $y_0 = IV$, a fixed initialisation vector, and for each block compute $y_i = C(b_i \,\|\, y_{i-1})$, where $512 + 256 = 768$ bits.
4. **Output** $H(M) = y_L$.

Each step takes a 512-bit block plus the 256-bit result of the previous step (the chaining value) and compresses them to 256 bits, so the chaining value plays the role of a running summary of everything hashed so far.

The construction's main theorem: **if $C$ is collision resistant, then $H$ is collision resistant** [@Merkle1990Certified; @Damgard1990Design]. Security for arbitrary-length inputs is thereby reduced to security of a single fixed-size function. The length field in the padding (Merkle–Damgård strengthening) is required for this proof. Without it, the reduction from $H$ to $C$ no longer goes through.
