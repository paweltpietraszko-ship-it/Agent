# Agent — customer-controlled AI workflow automation

**Cel produktu i portfolio:** zbudować działający, konfigurowalny demonstrator procesów biznesowych, który właściciel pokaże na Upwork jako dowód umiejętności projektowania, wdrażania i dostosowywania automatyzacji z AI. Nawet kilka płatnych zleceń byłoby osobistym sukcesem, ale ich zdobycie nie jest technicznym kryterium PASS.

**Najpierw przeczytaj [PRODUCT_GOAL_AND_ROADMAP.md](docs/PRODUCT_GOAL_AND_ROADMAP.md).** Następnie [CLAUDE.md](CLAUDE.md), [spec V0-A](docs/VERTICAL_V0A_FROZEN_SPEC.md) i [aktywne zadanie V0A-01](tasks/TASK_V0A_01_CORE_RECOVERY.md). `V0A-01` pozostaje pierwszym, ograniczonym taskiem technicznym, a nie definicją całego produktu.

## Zasada produktu

Klient kupuje **użyteczny proces biznesowy**, nie sam runtime. Agent ma działać w dwóch materialnie różnych konfiguracjach klientów bez przepisywania wspólnego CORE; Ridgeway jest tylko syntetycznym przykładem. Angielski jest językiem podstawowym produktu, a polski opcjonalnym drugim językiem interfejsu.

Chcemy pokazywać **kontrolę firmy nad przepływem danych i uprawnieniami**, nie składać nieudowadnialnej obietnicy „AI nigdy nie wykrada sekretów”. Model zewnętrzny może otrzymać wyłącznie dozwolony, minimalny pakiet zadaniowy; zakres transmisji musi dać się obejrzeć i przetestować. Przesłanie danych dostawcy modelu nie oznacza automatycznie publikacji w internecie, ale jest odrębnym przepływem danych i wymaga świadomej zgody/polityki klienta.

## Dla Claude Code — aktualna praca

1. Przeczytaj `docs/PRODUCT_GOAL_AND_ROADMAP.md` **tylko w zakresie celu, poufności i przyszłych kamieni milowych**. Nie implementuj całej mapy drogowej.
2. Przeczytaj `CLAUDE.md`, `docs/VERTICAL_V0A_FROZEN_SPEC.md` i `tasks/TASK_V0A_01_CORE_RECOVERY.md`.
3. Wykonaj **wyłącznie V0A-01**: FastAPI + PostgreSQL + SQLAlchemy/Alembic + DBOS + deterministyczny fake connector + 10 testów. Bez LLM, CRM, Gmaila, researchu, UI i pamięci EME.
4. Dostarcz uruchamialny kod, testy i `V0A01_REPORT.md`. Bez zgody na przejście do kolejnego zadania samodzielnie.

## Dokumenty

| Plik | Rola |
| --- | --- |
| `docs/PRODUCT_GOAL_AND_ROADMAP.md` | **Aktualny cel produktu, granice obietnicy poufności i mapa drogowa do portfolio** |
| `CLAUDE.md` | Kolejność dokumentów, zakres implementacji i sposób pracy |
| `docs/VERTICAL_V0A_FROZEN_SPEC.md` | Kontrakt techniczny pierwszego verticalu |
| `tasks/TASK_V0A_01_CORE_RECOVERY.md` | **Jedyne bieżące zadanie implementacyjne** |
| `docs/reference/ARCHITECT_LEDGER_v17.yaml` | Historia badań i decyzji, **nie backlog** |
| `docs/reference/PRODUCT_CANONICAL_2026-09-16.md` | Starszy kontekst produktu, nie aktualna mapa drogowa |
| `docs/reference/RIDGEWAY_CANONICAL_2026-09-16.md` | Starsza specyfikacja fikcyjnego klienta, nie uniwersalny schemat Agenta |

Nie czytaj całych historycznych dokumentów domyślnie ani nie podnoś wcześniejszych deklaracji „CURRENT” ponad nowe decyzje. Aktualną precedencję opisuje `CLAUDE.md`.
