# The Passport Page of a Country That Isn't There — a Republic of Leonida passport for make.fun

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/emasinves0-commits/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/emasinves0-commits/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

An entry for the make.fun bounty [The Passport Page of a Country That Isn't
There](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318):
one invented passport spread, drawn entirely in code.

## The document

A passport of the **Republic of Leonida**, issued in Vice City on 14 March
2024 to Elena R. Marlowe. The left page is the bio-data page — code-drawn
portrait, personal fields, a signature, and a machine-readable zone with
ICAO check digits computed in code (verified against the canonical ICAO
example). The right page carries six arrival and departure stamps telling
one coherent trip: Vice City → Port Gellhorn → Leonida Keys → Vice City,
2–16 June 2024, every stamp after the date of issue.

One piece of paperwork reveals the place: a printed notice states that
furry activity is prohibited in Leonida under the No Paws Clause (2026).
A small fee stamp records the $5 alligator crossing fee, paid at Port
Gellhorn.

## How the entry works

`main.py` (Python 3.13, stdlib + PIL only) draws the whole spread —
portrait, emblem, stamps, MRZ — and writes it deterministically to
`/output/entry.png` (1024×1024, under 1 MiB). No network, no input, no
timestamps; two runs are byte-identical. Fonts are vendored in `fonts/`
(Liberation Sans + DejaVu Sans Mono) so the program needs nothing from
the host system.

## Run it locally

    python3 main.py

`entry.png` is then the passport spread, exactly as the judge reads it.
