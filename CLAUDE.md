# CLAUDE.md — instrukcja implementera w repo Agent

## Jaki jest bieżący task

**V0A-01: Core Durable Action Lifecycle.** Zacznij od `tasks/TASK_V0A_01_CORE_RECOVERY.md`, ale wcześniej przeczytaj `docs/VERTICAL_V0A_FROZEN_SPEC.md`. Nie rozpoczynaj V0A-02, V0A-03 ani V0A-04. Brak zgody na Gmail, GHL, research, LLM, UI i EME w tej iteracji.

Owner podejmuje decyzje produktowe. ChatGPT pełni rolę architekta/koordynatora i odpowiada za scope/kontrakt; Claude Code implementuje; Codex lub równoważny niezależny tester audytuje. Techniczny PASS nie jest zgodą ownera na zmianę produktu.

## Precedencja dokumentów

1. `tasks/TASK_V0A_01_CORE_RECOVERY.md` — szczegółowe acceptance i zakres **tego** tasku.
2. `docs/VERTICAL_V0A_FROZEN_SPEC.md` — wiążące zasady całego verticalu.
3. Ten plik i `README.md` — sposób pracy, nawigacja, doprecyzowania organizacyjne.
4. `docs/reference/ARCHITECT_LEDGER_v17.yaml` — historia, uzasadnienia i alternatywy, **nie spec implementacji**.
5. `docs/reference/PRODUCT_CANONICAL_2026-09-16.md` oraz `docs/reference/RIDGEWAY_CANONICAL_2026-09-16.md` — zachowany kontekst wcześniejszego projektu, **nie aktywny kontrakt V0-A**.

Spec V0-A i task V0A-01 są późniejszymi decyzjami: wybrany kandydat runtime to DBOS + PostgreSQL (nie LangGraph); brak implementacji Ridgeway/GHL w V0A-01. Stare dokumenty zawierają własne deklaracje „CURRENT” — były aktualne w chwili sporządzenia, ale nie mogą zmieniać aktualnego tasku. Nie stosuj z nich historycznych ról, gate'ów, globalnej orkiestracji AI ani dodatkowych modułów. Konflikt nie daje implementerowi prawa do samodzielnego przeprojektowania kontraktu.

## Zasady pracy

- **ADOPT → CONFIGURE → WRITE.** Minimalnie wykorzystuj sprawdzone API bibliotek, nie buduj własnego frameworku orkiestracji.
- Realizuj wyłącznie wymagane zachowania i testy. Nie rozwijaj hipotetycznych edge case'ów w nowe podsystemy.
- Kiedy rozpoznasz niezgodność DBOS z wymaganiem, pokaż konkretny reprodukowalny przypadek i najmniejszą poprawkę; nie zmieniaj sam kontraktu.
- Model/fake connector nie może pisać własnych reguł authority ani maskować wyniku zewnętrznego. Przy niejednoznacznym external effect: UNKNOWN, bez ślepego retry.
- Event history w bazie to kanoniczne źródło rekonstrukcji akcji, nie log modelu.
- Testy są **zgodnością implementacji z zamrożonym kontraktem**, nie badaniem od nowa ogólnej prawdziwości zasad.
- Czytaj tylko potrzebne pliki z `docs/reference/`. Nie skanuj wielokrotnie całego repo i nie ładuj pełnego Ledgera do kontekstu bez konkretnego pytania.
- Nie dopisuj nowych wymagań lub warstw bezpieczeństwa bez konkretnego failure case związanego z V0A-01.

## Koniec tasku

Przedstaw `V0A01_REPORT.md` z komendami uruchomienia, wynikiem **T01–T10**, faktycznie sprawdzonymi restart/crash/race scenariuszami, znanymi ograniczeniami, odstępstwami i werdyktem PASS/FAIL dla fit DBOS. Niczego nie ogłaszaj jako przetestowane, jeśli nie zostało uruchomione. Nie przechodź do kolejnego tasku samoczynnie.

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
  → cytujesz wynik DOSŁOWNIE w BOARD.md (nigdy parafrazy) → status `READY_FOR_ARCHITECT`. FAIL naprawiasz;
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
