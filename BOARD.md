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
| HARNESS-STARTER-KIT | CC | Architekt | `task/HARNESS-STARTER-KIT` | `59e7e6c` | OWNER_DECISION_NEEDED | **Zestaw startowy harnessu z Roty (zlecenie OWNERA 2026-09-21), gotowy do przeglądu i decyzji o merge.** Zawartość: `harness/` (bramka `backend.py`, `guard.py`, `task_init.py`, szablon briefu, 60 testów samego harnessu), `.githooks/pre-commit`, `docs/PROCESS.md`, `AGENTS.md`, `ARCHITECT_START_HERE.md`, sekcja w `CLAUDE.md` (dopisana na końcu, istniejący tekst bez zmian), BOARD/ODLOZONE. Nowe względem Roty: ARCHITECT_REVIEW jako pierwszy audyt + Codex na kompletną jednostkę audytu (AUDIT_UNIT), poziomy LIGHT/STANDARD/CRITICAL, bramka mierzy commit a nie katalog roboczy, BRIEF_FROZEN, zakres katalogami (`app/**`), limity deklarowane w briefie. **DO ZROBIENIA PRZEZ ARCHITEKTA przed startem V0A-01:** (1) brief `tasks/TASK_V0A_01_CORE_RECOVERY.md` nie ma `TASK_SCOPE` ani `AUDIT_TIER` -- bramka zwróci FAIL (sprawdzone na prawdziwym briefie). Dopisz i zacommituj na `main` PRZED implementacją blok, np. (propozycja CC, nie decyzja): `AUDIT_TIER: CRITICAL`, `MAX_NEW_FILES: 30`, `TOTAL_LINES_THRESHOLD: 1500`, `TASK_SCOPE:` z pozycjami `app/**`, `migrations/**`, `tests/**`, `alembic.ini`, `pyproject.toml`, `V0A01_REPORT.md` (dopisz np. `docker-compose.yml`, jeśli PostgreSQL ma być uruchamiany z repo -- plik spoza listy = FAIL). (2) Uzupełnij `harness/critical_paths.txt`, gdy powstanie układ kodu (cykl życia akcji, konektor, migracje). (3) Przejrzyj `docs/PROCESS.md` sekcje 4-5. **Do potwierdzenia przez OWNERA:** (a) poziom LIGHT bez audytu Codexa; (b) `harness/FROZEN.lock` zamraża `docs/VERTICAL_V0A_FROZEN_SPEC.md` (zmiana = `guard freeze --recompute`). Świadomie NIE przeniesione z Roty: `where.py`, `session_log.py`, `CODEX_START_HERE.md` (scalone do AGENTS.md). Znane ograniczenie: kolejność etapów (np. brak ARCHITECT_REVIEW przed Codexem) nie jest jeszcze wymuszana mechanicznie -- to zadanie dla Maestro. |
