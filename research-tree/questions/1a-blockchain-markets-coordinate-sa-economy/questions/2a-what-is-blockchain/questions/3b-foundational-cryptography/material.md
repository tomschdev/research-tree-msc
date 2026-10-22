# What comprises the foundational cryptographic concepts of blockchain?

[@Narayanan2016Bitcoin] explains the mathematical foundations on which the majority of DLT systems are built.

## Cryptographic Hash Functions

Cryptographic hash funchtions (CHF) are fundamental mathematical primitives that provide data integrity, tamper-evidence, and trustless consensus. A hash function maps an input string of arbitrary size to a fixed-size output string e.g., 256 bit in case of SHA-256, in an efficiently computable manner.

For a CHF to be cryptographically secure, it must satisfy three core properties:
### Collision Resistance
A CHF is collision resistant if it is computationally infeasible to find two distinct inputs x != y that produce same output hash H(x) = H(y). Although collisions exist mathematically due to the Pigeonhole Principle and could theoretically be found in roughly 2^{128} operations via the Birthday Paradox, calculating this would take octillions of years on modern hardware.
- Pigeonhole Principle: a counting rule which states that if you have more inputs than outputs, atleast one output must be the subject of a collision for two or more inputs.
- Birthday Paradox: a probability phenomenon showing that finding a collision requires testing far fewer random inputs that intuitiely expected. Instead of trying all possible outputs, you onlt need to examine roughly the square root of the total output space. For exmaple, there are 365 days ina year. You onlty need 23 people ina room to reach >50% probability that two of them share a birthday. This is because you are checking pairs, rather than matching 1 birthday against the rest. Pricipally, becuase the number of distinct pairings grows quadratically with group size, finding a collisiosn requires examining only roughly the square root of the total possible output space. In the context of CHF, an ttacker onlt needs to test roughly 2^{128} random inputs to find two matching hashes outputted by a 256-bit hash function. 2^{128} is still exceptionally large and infeasible to brute force.

### Hiding
Given an output y = H(x), it is infeasible to recover x if x is chosen from a high min-entropy distribution

### Puzzle-Friendliness
For any output y, if a portion of the input i is chosen from a high min-entropy dsitribution, there is no solving strategy to find an input x such that H(i || x) element of Y significantly faster than brute-force random guessing
