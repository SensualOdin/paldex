# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

delegated: single self-contained index.html built from `_app_template.html` by `_assemble.py` (all data inline, ~13 MB, fully offline, deployed as static files on Vercel from GitHub main). Chosen by the assistant because the pipeline, offline guarantee, and 492-page static SEO layer all depend on it; the user said "whatever you think is best, just make it epic."

## Users

Palworld players (1.0 release, July 2026) — mid-session on a second monitor or phone, asking concrete questions: "what breeds into Anubis?", "where does Coralum Ore spawn?", "who's the best fire mount early game?", "what passives should I surgery onto this Pal?". Owner (George) shares it with friends and the wider community; many arrive once from search and must get value in seconds.

## Product Purpose

A free Palworld 1.0 companion: Paldex browser (299 Pals — stats, partner skills, movesets, drops, habitat heat maps), table-driven breeding calculator with instant family trees, curated + computed tier boards, item database (sources ↔ recipes), team/synergy/surgery planner with projected damage, and an interactive world map (13.8k markers, spawn layers, found-tracking, calculated farming routes). Success = a player answers their question faster and more trustworthily than on any competing site, then keeps the tab open.

## Positioning

Everything is computed from the game's own extracted tables (palcalc game files + paldb.cc datamines), verified against independent sources, and runs entirely client-side — offline, no ads, no accounts, no marker paywalls (competitors gate found-tracking behind $). Unique features: instant breeding family trees, calculated farming routes with numbered loops, surgery planner with projected stat tiers, one-box global search across Pals/items/passives/markers.

## Constraints

- All existing functionality, data, deep links (`#pal=`, `#item=`, `#tab=`, `#map=`), and localStorage keys (caught/favs/team/map progress) must survive the redesign.
- The 492-URL static SEO layer (pal/, item/, landing pages) links into the app; canonical URLs must not change.
- Pal/element/item art are Palworld game assets (embedded); no license to alter them.
- Heavy canvas map and 299-card grid must stay 60fps-usable on mid phones.

## Brand commitments

None locked. User: "everything is on the table" — the name "Palydex" and the retro Pokédex-device look are both replaceable if the direction earns it. (Domain palydex.com stays.)

## Accessibility

Existing baseline to preserve: keyboard navigation on grid + tabs, aria roles on tabs/cards, prefers-reduced-motion guards on all animation, night mode. 16px inputs on mobile.
