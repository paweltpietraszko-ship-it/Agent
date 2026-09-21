# CLAUDE.md — implementer guidance for Agent

**Na początku każdej sesji przeczytaj `CC_START_HERE.md` (pamięć i stan repo) — zanim cokolwiek zmienisz.**

## Najpierw cel produktu, potem bieżący task

Przeczytaj `docs/PRODUCT_GOAL_AND_ROADMAP.md` dla **celu i granic produktu**. Agent ma być działającym, English-first, możliwym do konfigurowania demonstratorem AI workflow automation dla portfolio freelancera na Upwork. Nawet kilka płatnych zleceń byłoby osobistym sukcesem ownera; nie projektuj platformy na wyrost. Ridgeway to tylko referencyjny fikcyjny klient. Kontrola danych i uprawnień musi być demonstrowalna, nie opieraj marketingu na absolutnej obietnicy „AI never leaks secrets”.

**Jedyny aktualny task: V0A-01 Core Durable Action Lifecycle.** Przeczytaj `docs/VERTICAL_V0A_FROZEN_SPEC.md` i `tasks/TASK_V0A_01_CORE_RECOVERY.md`. Nie zaczynaj V0A-02/03/04 ani dalszej mapy drogowej. Brak zgody na Gmail/GHL, CRM, research, LLM, UI i EME w tej iteracji.

Owner podejmuje decyzje produktowe. ChatGPT odpowiada za architekturę, koordynację i zakres; Claude Code implementuje; Codex lub równoważny niezależny tester audytuje. Techniczny PASS nie uprawnia do samodzielnego rozszerzania produktu.

## Precedencja: rozdziel cel od zakresu tasku

1. `docs/PRODUCT_GOAL_AND_ROADMAP.md` — **nadrzędny cel produktu, kryterium portfolio, English-first i granica obietnicy poufności**. Nie jest poleceniem implementacji wszystkich kamieni milowych naraz.
2. `tasks/TASK_V0A_01_CORE_RECOVERY.md` — szczegółowe acceptance, stack i dopuszczalny zakres **bieżącego tasku**.
3. `docs/VERTICAL_V0A_FROZEN_SPEC.md` — obowiązujące reguły techniczne verticalu, o ile nie kolidują z celem produktu.
4. `CLAUDE.md` i `README.md` — sposób pracy i nawigacja.
5. `docs/reference/ARCHITECT_LEDGER_v17.yaml` — historia, hipotezy, uzasadnienia; **nie jest specem implementacji ani aktywnym backlogiem**.
6. `docs/reference/PRODUCT_CANONICAL_2026-09-16.md`, `docs/reference/RIDGEWAY_CANONICAL_2026-09-16.md` — starszy kontekst; nie mogą przywrócić LangGraph, pełnego EME, trzy-rodzinnego verticalu lub reguł Ridgeway jako uniwersalnych wymagań.

Przykład historycznej kolizji: Ridgeway wskazywał LangGraph; V0A-01 ma przetestować DBOS + PostgreSQL i obowiązuje w tym tasku. Nie interpretuj starszego „CURRENT” jako nowszego od roadmapy datowanej 2026-09-21.

**Jeżeli nadrzędny cel ujawni konflikt ze szczegółowym taskiem, zatrzymaj daną niezgodną część i zgłoś konkretne rozstrzygnięcie architektowi/ownerowi; nie przerabiaj zadania samodzielnie.** Nie odkładaj raportowania sprzeczności do końca implementacji.

## Zasady pracy

- ADOPT → CONFIGURE → WRITE. Korzystaj z bibliotek i adapterów tam, gdzie spełniają przyjęty kontrakt; nie twórz własnego frameworku na zapas.
- Pisz wyłącznie bieżący mały task. Nie dodawaj warstw bezpieczeństwa, pluginów ani nowych ról bez konkretnego przypadku związanego z taskiem.
- Kod produktowy i przykład Ridgeway mają być rozdzielone; w V0A-01 nie implementuj Ridgeway w ogóle.
- Wynik modelu to kandydat, nie authority. Fałszywa przesłanka nie może cicho sterować istotnym działaniem; w tym konkretnym tasku nie ma jeszcze LLM ani evidence qualification.
- `PENDING -> COMMITTING` jest atomowym przejściem. `UNKNOWN` po niejednoznacznym external effect bez ślepego retry. Historia eventów jest kanoniczna, nie log LLM.
- Testuj zgodność kodu z kontraktem; nie testuj na nowo dojrzałych metod naukowych jako hipotez.
- Nie czytaj bez potrzeby wszystkich plików w `docs/reference/` ani całego repo wielokrotnie.
- Nie deklaruj sukcesu, którego nie potwierdzają rzeczywiście uruchomione testy.

## Zakończenie V0A-01

Dostarcz `V0A01_REPORT.md`: komendy uruchomienia, wyniki T01–T10, faktyczne restart/crash/race testy, ograniczenia i odchylenia; PASS/FAIL dla dopasowania DBOS do zamrożonego lifecycle. **Nie rozpoczynaj automatycznie kolejnego etapu**, nawet po PASS. Produkt staje się portfolio-ready dopiero według osobnych kryteriów w roadmapie, nie po przejściu tych 10 testów.

## Proces i harness (obowiązuje zawsze; szczegóły: `docs/PROCESS.md`)

Nie polegamy na Twojej pamięci — reguły, których złamanie byłoby incydentem, sprawdza skrypt. Nie omijaj ich.

- **Rola:** implementer i merytoryczny recenzent briefu. Nie jesteś architektem ani audytorem; nigdy nie
  zatwierdzasz własnej implementacji (PASS/FAIL kodu należy do niezależnego audytora).
- **Przed kodem:** przeczytaj brief. Brak `TASK_SCOPE` / `AUDIT_TIER`, niejasność albo pomysł, który uważasz za
  źle pomyślany = STOP, pytanie do Ownera przez `BOARD.md`. Nie zgaduj, nie implementuj „jak popadnie".
- **Start (raz na klon):** `git config core.hooksPath .githooks`. Na Task: `git switch -c task/<id>`,
  `python harness/task_init.py <id>`. Hook blokuje commit na `main` poza BOARD.md/ODLOZONE.md; przed commitem
  i tak sprawdź `git branch --show-current`.
- **Zakres:** tylko `TASK_SCOPE`. Potrzeba pliku spoza listy albo znalezisko „przy okazji" = zgłoś w
  `BOARD.md`/`ODLOZONE.md`, nie rób sam. Zgłoszenie błędu to nie jest wykonanie poprawki.
- **Dostawa:** małe commity → `python harness/backend.py <brief> <before_sha> <head_sha> tasks/<id>/backend_r<n>.txt`
  (before_sha = `git merge-base origin/main HEAD`, head_sha = `git rev-parse HEAD`; bramka odpala się też sama na GitHubie) → cytujesz wynik DOSŁOWNIE w BOARD.md (nigdy parafrazy) → status `READY_FOR_ARCHITECT`. FAIL naprawiasz;
  `WYMAGA_DECYZJI` należy do Ownera/architekta. Podaj adresata i czy branch jest wypchnięty (SHA).
- **Git:** przed twierdzeniem „zaimplementowane/brak" zrób `git fetch` i patrz na `origin/main`. Branche `task/*`
  wypychasz sam; do `main` wchodzisz wyłącznie po „zmerguj" Ownera i **od razu usuwasz** branch (zdalny i lokalny).
- **Owner nie czyta kodu:** pisz po polsku, prosto, per „ty". Zachowanie widoczne dla człowieka streść własnymi
  słowami i poczekaj na „tak, zgadza się" przed kodowaniem lub przekazaniem dalej.
- **Uczciwość dowodu:** raport = co uruchomiono i wynik; nie ogłaszaj niczego jako przetestowane, jeśli nie
  uruchomiono; nazwij ograniczenia. Repro kopiuje CAŁĄ realną konfigurację (nie „łagodniejsze" wartości domyślne).
- **Nie ruszaj** `harness/`, `.githooks/` ani zamrożonych plików z `harness/FROZEN.lock` — to własność
  Ownera/architekta.
- **Budżet:** wąskie testy tego, co zmieniłeś, nie pełna suita „na wszelki wypadek"; zbiorcze wywołania narzędzi.
