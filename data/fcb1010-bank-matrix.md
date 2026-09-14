# FCB1010 Bank / Switch Matrix

Generated from `fcb1010-patch-data.json`. Mesa Mark V:35 + Peavey Bandit
112 only (Marshall out as of 2026-09-14). Peavey on FCB1010 built-in
relay SWITCH1 and Switch-Track OUTA (both consolidated from
SWITCH2/OUTB). Banks 0/1 mix single-amp and stereo-combo tones per
song-section energy (clean vs dirty) rather than segregating by
category. Regenerate after any change to the JSON rather than
hand-editing this file.

## Bank 0 - Clean-oriented section

| Sw | Function | Mesa preset | Peavey | Switch-Track PC |
|----|----------|-------------|--------|------------------|
| 1 | Mesa Clean EQ-on (alone) | clean_eq_on | - | PC7 |
| 2 | Mesa Clean EQ-off (alone) | clean_eq_off | - | PC7 |
| 3 | Mesa Clean EQ-on + Peavey Clean | clean_eq_on | clean | PC1 |
| 4 | Mesa Clean EQ-off + Peavey Clean | clean_eq_off | clean | PC1 |
| 5 | Mesa Clean EQ-on + Peavey Dirty | clean_eq_on | dirty | PC1 |
| 6 | Mesa Clean EQ-off + Peavey Dirty | clean_eq_off | dirty | PC1 |
| 7 | All Mute (silence) | muted | - | PC7 |
| 8 | All Mute (silence) | muted | - | PC7 |
| 9 | All Mute (silence) | muted | - | PC7 |
| 10 | All Mute (silence) | muted | - | PC7 |

## Bank 1 - Dirty-oriented section

| Sw | Function | Mesa preset | Peavey | Switch-Track PC |
|----|----------|-------------|--------|------------------|
| 1 | Mesa Dirty EQ-on (alone) | dirty_eq_on | - | PC7 |
| 2 | Mesa Dirty EQ-off (alone) | dirty_eq_off | - | PC7 |
| 3 | Mesa Dirty EQ-on + Peavey Clean | dirty_eq_on | clean | PC1 |
| 4 | Mesa Dirty EQ-off + Peavey Clean | dirty_eq_off | clean | PC1 |
| 5 | Mesa Dirty EQ-on + Peavey Dirty | dirty_eq_on | dirty | PC1 |
| 6 | Mesa Dirty EQ-off + Peavey Dirty | dirty_eq_off | dirty | PC1 |
| 7 | All Mute (silence) | muted | - | PC7 |
| 8 | All Mute (silence) | muted | - | PC7 |
| 9 | All Mute (silence) | muted | - | PC7 |
| 10 | All Mute (silence) | muted | - | PC7 |

## Bank 3 - Single-amp reference (Mesa + Peavey)

| Sw | Function |
|----|----------|
| 1 | Mesa Clean, EQ on |
| 2 | Mesa Clean, EQ off |
| 3 | Mesa Dirty, EQ on |
| 4 | Mesa Dirty, EQ off |
| 5 | Peavey Clean |
| 6 | Peavey Dirty |
| 7 | All Mute (silence) |
| 8 | All Mute (silence) |
| 9 | All Mute (silence) |
| 10 | All Mute (silence) |

## Mesa preset PC numbers

Programmed directly onto Control Switcher (hold button 1 + button 4 while
its switches are in the target combination), confirmed working 2026-09-14:

- **PC1 = clean_eq_on**: Channel=Clean, Solo1=off, EQ=on
- **PC2 = clean_eq_off**: Channel=Clean, Solo1=off, EQ=off (featured/solo clean tone)
- **PC3 = dirty_eq_on**: Channel=Dirty, Solo1=off, EQ=on
- **PC4 = dirty_eq_off**: Channel=Dirty, Solo1=off, EQ=off
- **PC5 = muted**: Channel=Clean, Solo1=on (mute), EQ=on

Banks 2 and 4-8 open. See `data/fcb1010-patch-data.json` meta for full
notes (rig history, Switch-Track wiring, Peavey relay consolidation).
