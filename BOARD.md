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
| HARNESS-KIT-POSTMERGE | CC | Architekt | `main` | `cb728d4` | OWNER_DECISION_NEEDED | **Zestaw startowy harnessu jest zmergowany do `main`** (Owner: zmerguj, 2026-09-21) po 4 rundach audytu Codexa (r1-r3 FAIL naprawione, r4 PASS na exact SHA `b724256`; raporty w repo Roty `tasks/AGENT-HARNESS-KIT-AUDIT/`). Repo jest publiczne; na `main` regula blokuje force-push i usuwanie. **DO ZROBIENIA PRZEZ ARCHITEKTA przed startem V0A-01:** (1) brief `tasks/TASK_V0A_01_CORE_RECOVERY.md` nie ma `TASK_SCOPE` ani `AUDIT_TIER` -- bramka da FAIL. Dopisz i zacommituj na `main` PRZED implementacja (propozycja CC, nie decyzja): `AUDIT_TIER: CRITICAL`, `MAX_NEW_FILES: 30`, `TOTAL_LINES_THRESHOLD: 1500`, `TASK_SCOPE:` `app/**`, `migrations/**`, `tests/**`, `alembic.ini`, `pyproject.toml`, `V0A01_REPORT.md` (dopisz np. `docker-compose.yml`, jesli PostgreSQL ma startowac z repo). (2) Uzupelnij `harness/critical_paths.txt`, gdy powstanie uklad kodu. (3) Zasady bramki: zakres, zamrozone pliki i ochrona `harness/` `.github/` = FAIL; rozmiar plikow/funkcji, RATIO/TOTAL_LINES, poziom audytu = tylko WYMAGA_DECYZJI. **Otwarte po stronie CC:** bramka musi przepuszczac PR zmieniajacy wylacznie BOARD.md/ODLOZONE.md (bez briefu), dopiero wtedy wlaczamy na `main` wymog zielonego `gate` (zmiana `gate.yml` = audyt Codexa). Do tego czasu BOARD.md idzie prosto na `main`. |
