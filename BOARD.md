# BOARD.md — kolejka przekazań Architekt ↔ CC ↔ Codex

Jedyne wspólne miejsce przekazań. To dziennik techniczny, NIE źródło ustaleń produktowych (te są w briefie /
kontrakcie / decyzjach OWNERA). Zawsze `git pull` przed edycją: architekt i Codex piszą tu równolegle.
Bezpośredni commit na `main` dozwolony tylko dla BOARD.md i ODLOZONE.md.

Statusy (dokładnie pięć):

- `READY_FOR_ARCHITECT` — CC skończył Task (bramka PASS), czeka na ARCHITECT_REVIEW.
- `READY_FOR_CODEX` — jednostka audytu kompletna, wszystkie Taski CONFORMS, czeka na audyt.
- `CODEX_IN_PROGRESS` — Codex audytuje.
- `CODEX_REPORTED` — raport gotowy pod wskazaną ścieżką.
- `OWNER_DECISION_NEEDED` — proces stanął na decyzji OWNERA.

Nowy wiersz dopisuje autor przekazania; zmianę statusu wpisuje ten, kto kończy etap. Zamknięty wiersz
(merge/decyzja) usuwa ten, kto go zamyka — historia zostaje w `git log -p BOARD.md`.
W wierszu CC cytuje DOSŁOWNIE wynik `harness/backend.py` (nigdy parafrazy).

| ID | Autor | Odbiorca | Branch | Exact SHA | Status | Wiadomość |
|---|---|---|---|---|---|---|
