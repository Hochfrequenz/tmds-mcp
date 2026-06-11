# TMDS Bug Hunt Workflow

Read-only access to the Technical Master Data Service (TMDS). All tools are safe to call on Prod.

## Identifier reference

| ID | Format example | Used in |
|---|---|---|
| MeLo-ID | `DE1234567890123456789012345678901` (DE + 31 chars) | Messlokation, Netzverträge |
| MaLo-ID | `12345678901` (11 digits) | Marktlokation, Netzverträge |
| Netzvertrag-ID | UUID `xxxxxxxx-xxxx-...` | single Netzvertrag lookup |
| Zähler-ID | UUID | Zähler lookup |

## Scenario 1: Kundendaten falsch — Stammdaten prüfen

1. MeLo-ID known → `get_messlokation(melo_id)` — check base meter data
2. MaLo-ID known → `get_marktlokation(malo_id)` — check base market location data
3. `get_netzvertraege_for_melo(melo_id)` or `get_netzvertraege_for_malo(malo_id)` — check active contracts
4. Zähler-ID known → `get_zaehler(zaehler_id)` — inspect meter at current or historical keydate
5. Cross-check with BSS via bss-mcp: `get_ermittlungsauftraege_by_malo(malo_id)`

## Scenario 2: BSS hat keinen Datensatz für eine MaLo

Likely TMDS ↔ BSS inconsistency. Check:
1. `get_marktlokation(malo_id)` — does TMDS even know this MaLo?
2. `get_netzvertraege_for_malo(malo_id)` — does TMDS have active Netzverträge?
3. If TMDS has data but BSS has none: escalate — BSS might have missed an event

## Identifier conversion

TMDS holds both MeLo and MaLo. If you only have one:
- From MeLo → MaLo: `get_netzvertraege_for_melo(melo_id)` — each Netzvertrag contains the MaLo reference
- From MaLo → MeLo: `get_marktlokation(malo_id)` — contains linked MeLo references

## Common pitfalls

- `get_messlokation` returns `None`: MeLo-ID not in TMDS — check spelling, leading zeros, DE prefix
- `get_zaehler` with wrong keydate returns stale data — omit keydate for current state
- Empty Netzverträge list: check if MeLo/MaLo is in the correct service area (Netzgebiet)
