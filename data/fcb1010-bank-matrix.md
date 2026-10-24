# FCB1010 Bank / Switch Matrix

From `fcb1010-patch-data.json` as sent 2026-10-24 (history #24). Mesa Mark
V:35 + Peavey Bandit 112. Everything is in bank 0. Update this after any
change to the JSON.

Switch-Track: A = Peavey, B = Mesa. SWITCH1 = Peavey channel (closed =
dirty), SWITCH2 = Peavey FX loop (closed = on).

## Bank 0

| Sw | Sound | Switch-Track (ch2) | Mesa preset (ch1) | SWITCH1 Peavey ch | SWITCH2 Peavey loop |
|----|-------|--------------------|-------------------|-------------------|---------------------|
| 1 | Mesa clean + Peavey clean | PC5 A+B | PC1 clean_eq_on | open (clean) | closed (on) |
| 2 | Mesa clean + Peavey dirty | PC5 A+B | PC1 clean_eq_on | closed (dirty) | closed (on) |
| 3 | Mesa dirty + Peavey clean | PC5 A+B | PC3 dirty_eq_on | open (clean) | closed (on) |
| 4 | Mesa dirty + Peavey dirty | PC5 A+B | PC3 dirty_eq_on | closed (dirty) | closed (on) |
| 5 | Mute | PC7 Mute | PC5 muted | open (clean) | open (off) |
| 6 | Mesa clean alone | PC3 B | PC1 clean_eq_on | open (clean) | open (off) |
| 7 | Peavey clean alone | PC1 A | PC5 muted | open (clean) | closed (on) |
| 8 | Mesa dirty alone | PC3 B | PC3 dirty_eq_on | open (clean) | open (off) |
| 9 | Peavey dirty alone | PC1 A | PC5 muted | closed (dirty) | closed (on) |
| 10 | Mute | PC7 Mute | PC5 muted | open (clean) | open (off) |

Switches 1-4 are both amps, clean to dirty. 6-9 are one amp each, clean
before dirty. 5 and 10 are the only full mutes.
