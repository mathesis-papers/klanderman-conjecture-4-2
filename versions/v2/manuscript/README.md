# Isolated-top transfer systems

The note corrects the isolated-top transfer-system conjecture of Klanderman,
Lewis, Monson, Shibata and Van Niel. It gives elementary consequences of the
tulip theorem of DeMark, Hill, Kamel, Niu, Stoeckl, Van Niel and Yan, combined
with the hull results of Mazur, Osorno, Roitzheim, Santhanam, Van Niel and
Zapata Castro. The earlier cyclic compatibility criterion of Hill, Meng and
Li and the star-generation formula of Rubin are also credited.

## Contents and build

- `note.tex`: self-contained LaTeX with an inline bibliography.
- `note.pdf`: readable mathematical note.
- `verify.py` and `finite-check.json`: dependency-free exact finite checks.
- `metadata.json`: scientific description, creators and mathematical coverage.
- `LICENSE.txt`: CC BY 4.0.
- `MANIFEST.sha256`: SHA-256 member hashes in the source archive.

Build with Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, use a standard TeX distribution with `geometry`, `amsmath`,
`amssymb`, `amsthm`, `booktabs`, `array`, `fontenc`, `lmodern` and `hyperref`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The inline bibliography needs no separate BibTeX step. The source archive
contains every nonstandard source file needed by these commands.

## Mathematical coverage

Theorem 1 gives a self-contained derivation of the classification under the
two-component isolated-top hypotheses. Its compatibility criterion specializes
DeMark et al., arXiv:2604.00335v1, Propositions 2.21 and 3.17, using the
saturated-hull description of Mazur et al. Corollary 2 describes the lattice of compatible
greater systems as the conjugation-invariant order ideals of proper subgroups.
Corollary 3 proves the prime-order LSP criterion for every isolated-top system,
regardless of its number of components, and classifies the cosaturated cases.
It also reproves the connected-case result of Mazur et al. Corollary 4 gives
the exact obstruction for the proper-subgroup star.

The pinned Lean source is
https://github.com/the-omega-institute/trureturing/blob/8acba483bc80695fef00c6b8c491e2ae16d5145f/D5/S3/FiniteGroups/KlandermanConjecture42Refutation.lean
Its declaration
`D5.S3.FiniteGroups.KlandermanConjecture42Refutation.result`
states the negation of the original universal conjunction, using the quaternion
compatibility counterexample. `claim` fixes the original quantifiers,
`generated` is ordinary transfer generation, and `generated_star` identifies
the generated star relation. The arbitrary-group classification and its
corollaries are the written proofs in the note.

The finite checks enumerate every subgroup and every inclusion-refining
identity-containing relation on Q8, C2, C4, C8, C6, C2 x C2 and S3. They test
the transfer axioms, graph components, saturated hull, ordinary generation,
compatibility, order-ideal correspondence and the isolated-top and connected
consequences. Conjugation is included, in particular for S3. Run with Python 3:

```sh
python3 verify.py > recomputed.json
python3 -c 'import json; assert json.load(open("recomputed.json")) == json.load(open("finite-check.json"))'
```

The finite checks corroborate exactly these seven groups; the written proofs
establish the arbitrary finite-group statements. The source's bisaturated
shortest-path conjecture is outside the note's mathematical coverage.

The Frobenius-width and dihedral-complexity formulas cited in the coverage
section are the results of Chakravarthy and Ghosh, arXiv:2605.04780v1,
Theorems 3.2 and 4.11, respectively.

## Creators and license

Haobo Ma — ChronoAI Pte Ltd, Singapore.

Wenlin Zhang — National University of Singapore; ChronoAI Pte Ltd, Singapore.

Copyright 2026 Haobo Ma and Wenlin Zhang. CC BY 4.0 (`cc-by-4.0`).
