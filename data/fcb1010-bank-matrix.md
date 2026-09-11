# FCB1010 Bank / Switch Matrix

Generated from `fcb1010-patch-data.json` - the full 70-patch layout,
one footswitch (1-10) per column, one bank (0-6) per row group.
Regenerate after any change to the JSON rather than hand-editing this file.

| Sw | Bank 0: Isolated Tone-Building | Bank 1: Mesa Clean | Bank 2: Mesa Dirty | Bank 3: Marshall Clean | Bank 4: Marshall Dirty | Bank 5: Bandit Clean | Bank 6: Bandit Dirty |
|----|---|---|---|---|---|---|---|
| 1 | Mesa clean (alone) | Mesa clean (alone) | Mesa dirty (alone) | Marshall clean (alone) | Marshall dirty (alone) | Bandit clean (alone) | Bandit dirty (alone) |
| 2 | Mesa dirty (alone) | Mesa clean + Marshall clean | Mesa dirty + Marshall clean | Marshall clean + Mesa clean | Marshall dirty + Mesa clean | Bandit clean + Mesa clean | Bandit dirty + Mesa clean |
| 3 | Marshall clean (alone) | Mesa clean + Bandit clean | Mesa dirty + Bandit clean | Marshall clean + Bandit clean | Marshall dirty + Bandit clean | Bandit clean + Marshall clean | Bandit dirty + Marshall clean |
| 4 | Marshall dirty (alone) | Mesa clean + Marshall clean + Bandit clean | Mesa dirty + Marshall clean + Bandit clean | Marshall clean + Mesa clean + Bandit clean | Marshall dirty + Mesa clean + Bandit clean | Bandit clean + Mesa clean + Marshall clean | Bandit dirty + Mesa clean + Marshall clean |
| 5 | Bandit clean (alone) | Mesa clean + Marshall dirty | Mesa dirty + Marshall dirty | Marshall clean + Mesa dirty | Marshall dirty + Mesa dirty | Bandit clean + Mesa dirty | Bandit dirty + Mesa dirty |
| 6 | Bandit dirty (alone) | Mesa clean + Marshall clean + Bandit dirty | Mesa dirty + Marshall clean + Bandit dirty | Marshall clean + Mesa clean + Bandit dirty | Marshall dirty + Mesa clean + Bandit dirty | Bandit clean + Mesa clean + Marshall dirty | Bandit dirty + Mesa clean + Marshall dirty |
| 7 | All mute (silence, amps set clean for lower standing noise) | Mesa clean + Bandit dirty | Mesa dirty + Bandit dirty | Marshall clean + Bandit dirty | Marshall dirty + Bandit dirty | Bandit clean + Marshall dirty | Bandit dirty + Marshall dirty |
| 8 | All mute (silence, amps set clean for lower standing noise) | Mesa clean + Marshall dirty + Bandit clean | Mesa dirty + Marshall dirty + Bandit clean | Marshall clean + Mesa dirty + Bandit clean | Marshall dirty + Mesa dirty + Bandit clean | Bandit clean + Mesa dirty + Marshall clean | Bandit dirty + Mesa dirty + Marshall clean |
| 9 | All mute (silence, amps set clean for lower standing noise) | Mesa clean + Marshall dirty + Bandit dirty | Mesa dirty + Marshall dirty + Bandit dirty | Marshall clean + Mesa dirty + Bandit dirty | Marshall dirty + Mesa dirty + Bandit dirty | Bandit clean + Mesa dirty + Marshall dirty | Bandit dirty + Mesa dirty + Marshall dirty |
| 10 | All mute (silence, amps set clean for lower standing noise) | All mute (silence, amps set clean for lower standing noise) | All mute (silence, amps set clean for lower standing noise) | All mute (silence, amps set clean for lower standing noise) | All mute (silence, amps set clean for lower standing noise) | All mute (silence, amps set clean for lower standing noise) | All mute (silence, amps set clean for lower standing noise) |

All 70 switch positions across banks 0-6 are populated; nothing is left empty.
Banks 7-9 are open, reserved for a future performance/favorites bank.
