"""
5_KarlWeierstrass_NEXT_frekvencija_v2 — agregacija kombinacija iz 12 NEXT modela
i frekvencija pojavljivanja brojeva 1..39.

Nadogradnja v1 (4_KarlWeierstrass_NEXT_frekvencija.py) — dodato 4 nova POGODNO
modela koja dolaze iz selekcije (NEXT9..NEXT12):
  - NEXT9_2a3j   (Brown + RQA-DET)
  - NEXT10_2a3k  (Brown + Variance ratio)
  - NEXT11_2b3f  (Hurst + exp-ACF)
  - NEXT12_2b3h  (Hurst + DFA)

Citam TXT izlaze iz svih 12 modela, vadimo svaki tuple (a, b, c, d, e, f, g)
sa 7 brojeva 1..39, brisem duplikate unutar fajla, izbacujemo placeholder
(1,2,3,4,5,6,7) i racunam ukupno frekvenciju.

Output:
  print u konzolu
  5_KarlWeierstrass_NEXT_frekvencija_v2.txt
  5_KarlWeierstrass_NEXT_frekvencija_v2.png
"""

import os
import re
from collections import Counter

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
TXT_OUT = os.path.join(HERE, "5_KarlWeierstrass_NEXT_frekvencija_v2.txt")
PNG_OUT = os.path.join(HERE, "5_KarlWeierstrass_NEXT_frekvencija_v2.png")

# (label, fajl, expected_count)
# Expected je broj kombinacija POSLE dedupliciranja i izbacivanja placeholder-a (1..7).
# Stare 8 (NEXT1..NEXT8) — fiksno po dizajnu.
# Nove 4 (NEXT9..NEXT12) — main + z-grid kandidati, neki kolapsiraju (duplikat / placeholder).
NEXT_FILES = [
    ("NEXT1",  "3_KarlWeierstrass_NEXT1_2a3b.txt", 4),
    ("NEXT2",  "3_KarlWeierstrass_NEXT2_2a3c.txt", 4),
    ("NEXT3",  "3_KarlWeierstrass_NEXT3_2a3d.txt", 4),
    ("NEXT4",  "3_KarlWeierstrass_NEXT4_2a3e.txt", 6),
    ("NEXT5",  "3_KarlWeierstrass_NEXT5_2b3a.txt", 3),
    ("NEXT6",  "3_KarlWeierstrass_NEXT6_2b3b.txt", 3),
    ("NEXT7",  "3_KarlWeierstrass_NEXT7_2b3e.txt", 3),
    ("NEXT8",  "3_KarlWeierstrass_NEXT8_2c3b.txt", 3),
    ("NEXT9",  "5_KarlWeierstrass_NEXT9_2a3j.txt", 5),
    ("NEXT10", "5_KarlWeierstrass_NEXT10_2a3k.txt", 5),
    ("NEXT11", "5_KarlWeierstrass_NEXT11_2b3f.txt", 4),
    ("NEXT12", "5_KarlWeierstrass_NEXT12_2b3h.txt", 3),
]

PLACEHOLDER = (1, 2, 3, 4, 5, 6, 7)
N_MIN, N_MAX = 1, 39
K_PICK = 7

COMBO_RE = re.compile(
    r"\(\s*(\d{1,2})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*,"
    r"\s*(\d{1,2})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*\)"
)


def extract_combos(text):
    """Vadi sve 7-tuple-ove iz teksta, vraca unique listu (po prvom pojavljivanju)."""
    seen = set()
    out = []
    for match in COMBO_RE.finditer(text):
        combo = tuple(sorted(int(x) for x in match.groups()))
        if any(v < N_MIN or v > N_MAX for v in combo):
            continue
        if len(set(combo)) != K_PICK:
            continue
        if combo == PLACEHOLDER:
            continue
        if combo in seen:
            continue
        seen.add(combo)
        out.append(combo)
    return out


all_combos = []
per_file_rows = []
mismatch_notes = []

for label, fname, expected in NEXT_FILES:
    path = os.path.join(HERE, fname)
    if not os.path.exists(path):
        mismatch_notes.append(f"  {label}: fajl ne postoji -> {path}")
        per_file_rows.append((label, fname, expected, 0, []))
        continue
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    combos = extract_combos(text)
    per_file_rows.append((label, fname, expected, len(combos), combos))
    all_combos.extend(combos)
    if expected is not None and len(combos) != expected:
        mismatch_notes.append(
            f"  {label}: ocekivano {expected}, pronadjeno {len(combos)}"
        )

total = len(all_combos)

counter = Counter()
for combo in all_combos:
    for num in combo:
        counter[num] += 1

freq_rows = sorted(counter.items(), key=lambda kv: (-kv[1], -kv[0]))


# ─── ispis ─────────────────────────────────────────────────────────
lines = []
lines.append("5_KarlWeierstrass_NEXT_frekvencija_v2")
lines.append("=" * 60)
lines.append("")
lines.append("Izvor: 12 NEXT TXT fajlova (8 originalna + 4 nova POGODNO modela).")
lines.append("Placeholder (1,2,3,4,5,6,7) izbacen, duplikati unutar fajla obrisani.")
lines.append("")
lines.append("Kombinacije po fajlu:")
lines.append("-" * 60)
for label, fname, expected, got, combos in per_file_rows:
    if expected is None:
        status = f"({got} kombinacija — varijabilno)"
    else:
        status = "OK" if got == expected else f"MISMATCH (ocekivano {expected})"
    lines.append(f"{label}  [{fname}]  combos: {got}  {status}")
    for combo in combos:
        lines.append(f"    {combo}")
    lines.append("")

lines.append("-" * 60)
lines.append(f"UKUPNO jedinstvenih kombinacija (bez placeholder-a): {total}")
lines.append("")

if mismatch_notes:
    lines.append("Napomena - razlika u broju kombinacija:")
    lines.extend(mismatch_notes)
    lines.append("")

lines.append("Frekvencija pojavljivanja brojeva 1..39 (sort: count desc, broj desc):")
lines.append("-" * 60)
lines.append(f"  {'rang':<6}{'broj':>6}{'count':>10}")
for rank, (num, cnt) in enumerate(freq_rows, start=1):
    lines.append(f"  {rank:<6}{num:>6}{cnt:>10}")

missing = [n for n in range(N_MIN, N_MAX + 1) if n not in counter]
if missing:
    lines.append("")
    lines.append(f"Brojevi bez pojavljivanja ({len(missing)}): {missing}")

text = "\n".join(lines) + "\n"
print(text)

with open(TXT_OUT, "w", encoding="utf-8") as f:
    f.write(text)

print(f"TXT saved -> {TXT_OUT}")
print()


# ─── tabela frekvencije kao PNG ──────────────────────────────────────
table_headers = ["rang", "broj", "count"]
table_rows = [[str(rank), str(num), str(cnt)]
              for rank, (num, cnt) in enumerate(freq_rows, start=1)]

max_count = max((cnt for _, cnt in freq_rows), default=1)

fig, ax = plt.subplots(figsize=(7, 12))
ax.axis("off")
ax.set_title(
    f"Frekvencija pojavljivanja brojeva 1..39\n"
    f"(12 NEXT modela: 8 originalna + 4 nova, {total} jedinstvenih kombinacija)",
    fontsize=13,
    fontweight="bold",
    pad=14,
)

table = ax.table(
    cellText=table_rows,
    colLabels=table_headers,
    colWidths=[0.18, 0.20, 0.22],
    cellLoc="center",
    loc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.0, 1.25)

for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor("#444444")
    cell.set_linewidth(0.5)
    if row == 0:
        cell.set_facecolor("#1f2937")
        cell.set_text_props(color="white", weight="bold")
        cell.set_height(cell.get_height() * 1.1)
    else:
        cnt = int(table_rows[row - 1][2])
        shade = 0.25 + 0.60 * (cnt / max_count)
        cell.set_facecolor((1.0 - 0.55 * shade, 1.0 - 0.20 * shade, 1.0 - 0.05 * shade))
        if col == 2:
            cell.set_text_props(weight="bold")

fig.tight_layout()
plt.show()
fig.savefig(PNG_OUT, dpi=200, bbox_inches="tight")
print(f"PNG saved -> {PNG_OUT}")
print()


"""
5_KarlWeierstrass_NEXT_frekvencija_v2
============================================================

Izvor: 12 NEXT TXT fajlova (8 originalna + 4 nova POGODNO modela).
Placeholder (1,2,3,4,5,6,7) izbacen, duplikati unutar fajla obrisani.

Kombinacije po fajlu:
------------------------------------------------------------
NEXT1  [3_KarlWeierstrass_NEXT1_2a3b.txt]  combos: 4  OK
    (1, x, 13, y, 31, z, 39)
    (2, x, 14, y, 25, z, 39)
    (3, x, 9, y, 23, z, 37)
    (4, x, 19, y, 23, z, 32)

NEXT2  [3_KarlWeierstrass_NEXT2_2a3c.txt]  combos: 4  OK
    (1, x, 12, y, 16, z, 39)
    (1, x, 11, y, 22, z, 32)
    (3, x, 23, y, 29, z, 37)
    (5, x, 16, y, 29, z, 37)

NEXT3  [3_KarlWeierstrass_NEXT3_2a3d.txt]  combos: 4  OK
    (2, x, 4, y, 11, z, 25)
    (2, x, 5, y, 20, z, 26)
    (4, x, 13, y, 22, z, 34)
    (6, x, 17, y, 21, z, 34)

NEXT4  [3_KarlWeierstrass_NEXT4_2a3e.txt]  combos: 6  OK
    (3, x, 21, y, 26, z, 33)
    (1, x, 15, y, 18, z, 37)
    (2, x, 12, y, 21, z, 38)
    (4, x, 6, y, 24, z, 31)
    (6, x, 11, y, 23, z, 26)
    (7, x, 20, y, 24, z, 32)

NEXT5  [3_KarlWeierstrass_NEXT5_2b3a.txt]  combos: 3  OK
    (1, x, 6, y, 27, z, 38)
    (1, x, 23, y, 25, z, 38)
    (2, x, 13, y, 28, z, 38)

NEXT6  [3_KarlWeierstrass_NEXT6_2b3b.txt]  combos: 3  OK
    (1, x, 6, y, 15, z, 27)
    (1, x, 25, y, 31, z, 34)
    (2, x, 21, y, 34, z, 36)

NEXT7  [3_KarlWeierstrass_NEXT7_2b3e.txt]  combos: 3  OK
    (1, x, 16, y, 21, z, 36)
    (2, x, 11, y, 27, z, 36)
    (4, x, 9, y, 14, z, 25)

NEXT8  [3_KarlWeierstrass_NEXT8_2c3b.txt]  combos: 3  OK
    (1, x, 14, y, 18, z, 26)
    (2, x, 19, y, 29, z, 37)
    (4, x, 13, y, 16, z, 35)

NEXT9  [5_KarlWeierstrass_NEXT9_2a3j.txt]  combos: 5  OK
    (1, x, 9, y, 17, z, 26)
    (1, x, 5, y, 11, z, 31)
    (3, x, 7, y, 19, z, 32)
    (6, x, 12, y, 24, z, 38)
    (7, x, 12, y, 22, z, 30)

NEXT10  [5_KarlWeierstrass_NEXT10_2a3k.txt]  combos: 5  OK
    (1, x, 21, y, 34, z, 38)
    (1, x, 5, y, 7, z, 38)
    (2, x, 13, y, 33, z, 38)
    (3, x, 10, y, 27, z, 34)
    (4, x, 15, y, 17, z, 34)

NEXT11  [5_KarlWeierstrass_NEXT11_2b3f.txt]  combos: 4  OK
    (1, x, 12, y, 25, z, 38)
    (1, x, 8, y, 21, z, 37)
    (1, x, 10, y, 25, z, 38)
    (1, x, 19, y, 30, z, 38)

NEXT12  [5_KarlWeierstrass_NEXT12_2b3h.txt]  combos: 3  OK
    (1, x, 17, y, 24, z, 34)
    (3, x, 5, y, 14, z, 32)
    (4, x, 9, y, 32, z, 39)

------------------------------------------------------------
UKUPNO jedinstvenih kombinacija (bez placeholder-a): 47

Frekvencija pojavljivanja brojeva 1..39 (sort: count desc, broj desc):
------------------------------------------------------------
  rang    broj     count
  1          1        19
  2          x        16
  3         21        14
  4          y        13
  5          z        13
  6         38        12
  7         37        10
  8         32        10
  9         24        10
  10         2        10
  11        34         9
  12        20         9
  13        19         9
  14        17         9
  15        16         9
  16        15         9
  17        10         9
  18         7         9
  19         5         9
  20         3         9
  21        13         8
  22        11         8
  23         9         8
  24        30         7
  25        26         7
  26        23         7
  27        31         6
  28        29         6
  29        28         6
  30        27         6
  31        14         6
  32        12         6
  33         8         6
  34        35         5
  35        22         5
  36        18         5
  37        39         4
  38        36         3
  39        33         3

TXT saved -> /5_KarlWeierstrass_NEXT_frekvencija_v2.txt

PNG saved -> /5_KarlWeierstrass_NEXT_frekvencija_v2.png
"""




"""
NEXT1 (4 kombinacije):

(1, 6, 13, 24, 31, 37, 39) — main
(2, 6, 14, 20, 25, 38, 39) — z=0.43
(3, 8, 9, 17, 23, 30, 37) — z=0.84
(4, 16, 19, 20, 23, 28, 32) — z=1.28
NEXT2 (4 kombinacije):

(1, 10, 12, 15, 16, 32, 39) — main
(1, 8, 11, 21, 22, 25, 32) — q=0.50
(3, 13, 23, 24, 29, 30, 37) — q=0.75
(5, 13, 16, 28, 29, 35, 37) — q=0.90
NEXT3 (4 kombinacije):

(2, 3, 4, 7, 11, 21, 25) — main
(2, 3, 5, 10, 20, 23, 26) — q=0.50
(4, 6, 13, 18, 22, 32, 34) — q=0.75
(6, 11, 17, 19, 21, 27, 34) — q=0.90
NEXT4 (6 kombinacija):

(3, 20, 21, 25, 26, 29, 33) — main
(1, 6, 15, 17, 18, 25, 37) — q=0.10
(2, 5, 12, 19, 21, 33, 38) — q=0.25
(4, 5, 6, 15, 24, 29, 31) — q=0.50
(6, 7, 11, 17, 23, 25, 26) — q=0.75
(7, 19, 20, 23, 24, 25, 32) — q=0.90
NEXT5 (3 kombinacije):

(1, 4, 6, 21, 27, 35, 38) — z=0.43
(1, 22, 23, 24, 25, 31, 38) — z=0.84
(2, 12, 13, 25, 28, 31, 38) — z=1.28
NEXT6 (3 kombinacije):

(1, 4, 6, 10, 15, 20, 27) — z=0.43
(1, 19, 25, 28, 31, 32, 34) — z=0.84
(2, 11, 21, 28, 34, 35, 36) — z=1.28
NEXT7 (3 kombinacije):

(1, 7, 16, 18, 21, 24, 36) — z=0.43
(2, 9, 11, 16, 27, 34, 36) — z=0.84
(4, 5, 9, 10, 14, 21, 25) — z=1.28
NEXT8 (3 kombinacije):

(1, 10, 14, 16, 18, 20, 26) — z=0.43
(2, 15, 19, 22, 29, 32, 37) — z=0.84
(4, 8, 13, 15, 16, 25, 35) — z=1.28
Ukupno: 30 kombinacija.



NEXT9 (5 kombinacija):

(1, 6, 9, 10, 17, 18, 26) — main
(1, 3, 5, 8, 11, 17, 31) — q=0.50
(3, 5, 7, 14, 19, 25, 32) — q=0.70
(6, 7, 12, 15, 24, 26, 38) — q=0.85
(7, 9, 12, 13, 22, 27, 30) — q=0.95
(q=0.05 → placeholder 1-7, otpada) → 5 ✓ slaže se sa tobom

NEXT10 — ja brojim 5, ti si rekao 4:

(1, 17, 21, 30, 34, 35, 38) — main
(1, 4, 5, 6, 7, 16, 38) — z=-0.43
(2, 10, 13, 21, 33, 37, 38) — z=0.43
(3, 9, 10, 24, 27, 30, 34) — z=0.84
(4, 11, 15, 16, 17, 25, 34) — z=1.28
(z=-1.28 → placeholder, z=0.00 → duplikat main) → 5, ne 4 ❗

NEXT11 (4 kombinacije):

(1, 2, 12, 19, 25, 28, 38) — main
(1, 4, 8, 14, 21, 24, 37) — z=0.43
(1, 6, 10, 20, 25, 29, 38) — z=0.84
(1, 9, 19, 21, 30, 37, 38) — z=1.28
(z=-1.28 → placeholder, z=0.00 → duplikat main) → 4 ✓ slaže se sa tobom

NEXT12 (3 kombinacije):

(1, 15, 17, 20, 24, 26, 34) — z=0.43
(3, 4, 5, 7, 14, 30, 32) — z=0.84
(4, 8, 9, 21, 32, 37, 39) — z=1.28


UKUPNO 47 kombinacija.
"""
