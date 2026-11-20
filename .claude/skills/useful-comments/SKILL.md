---
name: useful-comments
description: Write a comment only when it says something the code cannot. Use before adding or keeping any comment, in any language or file (Rust, Python, JS, shell, YAML, Makefile).
---

A comment earns its place only if it says something a reader cannot get by
reading the code. The bar is high: most functions need none. If the code, a
test, the file name or the name of the thing already says it, there is no
comment.

## Keep

- **Why:** the reason for a choice that the code alone does not show.
  `// Integer weights: the same result natively and in WASM, no float rounding.`
- **A pitfall:** what breaks if someone "simplifies" it.
  `// Must stay outside the timed region: the WASM allocator takes a global lock.`
- **A reference:** where a value or method comes from (paper, algorithm, spec). Never an ADR
  number: the ADRs explain decisions, the code comment says what the reader needs here.
  `// SplitMix64 (Steele, Lea and Flood, 2014); constants from the reference C code.`
- **A non-obvious unit or invariant:** `// nanoseconds per pass`, `// rows are pitch bytes apart`.

## Never

- Restating the code: `// increment i`, `# install dependencies` above `pip install`.
- Restating the signature or a property a test already shows:
  `/// The checksum of several slices hashed one after the other, as if concatenated.`
  above `of_slices`, when `slices_hash_like_their_concatenation` tests exactly that.
- Restating the file or block name: `# CI workflow` at the top of `ci.yml`,
  `// Tests` above `mod tests`.
- Statements about the project that belong in a README: `# CI never produces measurement results.`
- Banners, separators, dates, author names, "added by", "TODO later" without a ticket.
- Commented-out code.

## Check

For every comment, read it and ask: "if I delete it, does a reader lose
information they cannot get from the next lines?" If not, delete it. When
copying code from the working repository, keep its comments unless they fail
this check or point to a document that is not in this repository.
