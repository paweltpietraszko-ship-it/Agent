# Agent — Vertical V0-A

**Status:** dokumentacja i kontrakt pierwszego verticalu; brak zaimplementowanego produktu. To nowe repo nie jest kontynuacją Elnath Code.

## Zacznij tutaj (Claude Code)

1. Przeczytaj [CLAUDE.md](CLAUDE.md), następnie [zamrożony spec V0-A](docs/VERTICAL_V0A_FROZEN_SPEC.md) i [aktywne zadanie V0A-01](tasks/TASK_V0A_01_CORE_RECOVERY.md).
2. Wykonuj **wyłącznie V0A-01**. Pierwszy etap: Python + FastAPI + PostgreSQL + SQLAlchemy/Alembic + DBOS + deterministyczny fake connector + 10 acceptance tests. Bez LLM, researchu, Gmaila, UI i pamięci EME.
3. Gdy pojawia się konflikt pomiędzy dokumentami, obowiązuje kolejność z `CLAUDE.md`. Nie dopowiadaj decyzji produktowych na podstawie historycznych materiałów.
4. Wynik implementacji: działający kod, testy i krótki `V0A01_REPORT.md` z komendami, wynikami, ograniczeniami i ewentualnym FAIL. Nie zmieniaj kontraktu, żeby uzyskać PASS.

## Mapa dokumentów

| Plik | Rola |
| --- | --- |
| `CLAUDE.md` | Zasady pierwszeństwa i ograniczenia implementera |
| `docs/VERTICAL_V0A_FROZEN_SPEC.md` | Obowiązujący kontrakt całego verticalu |
| `tasks/TASK_V0A_01_CORE_RECOVERY.md` | **Jedyne aktywne zadanie do napisania teraz** |
| `docs/reference/ARCHITECT_LEDGER_v17.yaml` | Historia rozumowania i odrzuconych alternatyw; **nie jest bieżącą listą zadań** |
| `docs/reference/PRODUCT_CANONICAL_2026-09-16.md` | Historyczny szerszy kontekst produktu; nie nadpisuje decyzji V0-A |
| `docs/reference/RIDGEWAY_CANONICAL_2026-09-16.md` | Historyczna specyfikacja fikcyjnego Customer 01; V0A-01 **nie implementuje Ridgeway/GHL** |

Dokumenty w `docs/reference/` zachowano bez zmian jako źródła. Nie czytaj ich wszystkich domyślnie i nie włączaj do kontekstu całej historii. Jeśli aktywne zadanie wymaga konkretnego dawnego ustalenia, przeczytaj tylko potrzebny fragment i zachowaj aktualną precedencję.

## Jednoznaczny zakres

V0-A w przyszłości obejmie `Research & Follow-up`; V0A-01 ma sfalsyfikować *wyłącznie* trwałość sześciostanowego cyklu akcji z fake connector. Dołożenie modelu, drugiego agenta, pełnej EME czy GHL w tym tasku jest naruszeniem kontraktu.
