# FCB1010 Bank / Switch Matrix

From `fcb1010-patch-data.json`. Mesa Mark V:35 + Peavey Bandit 112.
Everything is in bank 0. Update this after any change to the JSON.

Switch-Track: A = Peavey, B = Mesa. SWITCH1 = Peavey channel (closed =
dirty), SWITCH2 = Peavey FX loop (closed = on). Daisy = program change on ch3
(127 = dry, no patch).

## Bank 0

| Sw | Sound | Switch-Track (ch2) | Mesa preset (ch1) | SWITCH1 Peavey ch | SWITCH2 Peavey loop | Daisy (ch3) |
|----|-------|--------------------|-------------------|-------------------|---------------------|-------------|
| 1 | Mesa clean + Peavey clean | PC5 A+B | PC1 clean_eq_on | open (clean) | closed (on) | PC127 dry |
| 2 | Mesa clean + Peavey dirty | PC5 A+B | PC1 clean_eq_on | closed (dirty) | closed (on) | PC127 dry |
| 3 | Mesa dirty + Peavey clean | PC5 A+B | PC3 dirty_eq_on | open (clean) | closed (on) | PC127 dry |
| 4 | Mesa dirty + Peavey dirty | PC5 A+B | PC3 dirty_eq_on | closed (dirty) | closed (on) | PC127 dry |
| 5 | Mute | PC7 Mute | PC5 muted | open (clean) | open (off) | PC127 dry |
| 6 | Mesa clean alone | PC3 B | PC1 clean_eq_on | open (clean) | open (off) | PC127 dry |
| 7 | Peavey clean alone | PC1 A | PC5 muted | open (clean) | closed (on) | PC127 dry |
| 8 | Mesa dirty alone | PC3 B | PC3 dirty_eq_on | open (clean) | open (off) | PC127 dry |
| 9 | Peavey dirty alone | PC1 A | PC5 muted | closed (dirty) | closed (on) | PC127 dry |
| 10 | Mute | PC7 Mute | PC5 muted | open (clean) | open (off) | PC127 dry |

Switches 1-4 are both amps, clean to dirty. 6-9 are one amp each, clean
before dirty. 5 and 10 are the only full mutes.
