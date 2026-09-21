# PROCESS — jak w tym repo modele dowożą działający program

Ten plik opisuje SPOSÓB PRACY. Nie zmienia produktu ani kontraktu Tasku (te są w `docs/VERTICAL_*`
i `tasks/`). Przy konflikcie obowiązuje kolejność z `CLAUDE.md`.

## 1. Zasada nadrzędna

Nie liczymy na to, że model „będzie pamiętał". Reguły, których złamanie byłoby incydentem, sprawdza
**skrypt** (`harness/`, hook w `.githooks/`), a nie zdanie w pliku. Proza zostaje tylko dla osądu:
projekt, sens testu, jakość sformułowań. Tło: [DETERMINISM_PATTERNS.md](DETERMINISM_PATTERNS.md).

## 2. Role — nikt nie zatwierdza własnej pracy

| Rola | Kto | Robi | Nie robi |
|---|---|---|---|
| **Owner** | Paweł | decyzje produktowe, „zmerguj" | nie czyta kodu; dostaje prosty polski |
| **Architekt** | ChatGPT (czyta GitHub) | brief/kontrakt, ARCHITECT_REVIEW | nie koduje, nie wystawia PASS kodu |
| **Implementer** | Claude Code | recenzja merytoryczna briefu, kod, bramka `backend.py` | nie audytuje własnej pracy, nie merguje bez „zmerguj" |
| **Audytor** | Codex (lub niezależny odpowiednik) | niezależny audyt exact SHA, jedyny PASS/FAIL kodu | nie projektuje produktu, nie naprawia kodu |

## 3. Przepływ jednego Tasku

1. Owner ustala zachowanie prostym językiem. Architekt zapisuje brief wg `harness/templates/brief.md`,
   Owner akceptuje, brief trafia na `main` **zanim** ruszy implementacja (potem jest zamrożony).
2. CC robi krótką recenzję merytoryczną briefu (sens, zakres, luki). Niejasne = pyta, nie zgaduje.
3. CC: `git config core.hooksPath .githooks` (raz na klon), `git switch -c task/<id>`,
   `python harness/task_init.py <id>`. Implementuje tylko `TASK_SCOPE`, małymi commitami.
4. **Bramka** odpala się **sama na GitHubie** po każdym pushu na `task/*` (`.github/workflows/gate.yml`) —
   nie zależy od tego, czy CC pamięta ją uruchomić. Brief musi leżeć w `tasks/<id>.md` albo
   `tasks/<id>/brief.md`, a SHA bazowy w `tasks/<id>/repo_before.hash` (robi to `task_init.py`).
   Lokalnie ten sam skrypt: `python harness/backend.py <brief> <before_sha> <head_sha> tasks/<id>/backend_r<n>.txt`.
   Wynik cytowany dosłownie w BOARD.md. FAIL (czerwony) = poprawka. WYMAGA_DECYZJI (żółte ostrzeżenie,
   Action nie blokuje) = decyzja Ownera/architekta, nie CC.
   Bazą pomiaru jest punkt odejścia brancha od `main` (`git merge-base`), liczony przez workflow, a nie
   wartość zapisana w repo — inaczej model mógłby przesunąć bazę i ukryć wcześniejsze commity (`BASE`).
   Brief czytany jest z commita, nie z katalogu roboczego. Symlinki w zmianach = FAIL.
   Wzorzec `**` oznacza „zero lub więcej poziomów katalogu" (decyzja Ownera): `app/**/*.py` obejmuje `app/x.py` i `app/sub/x.py`.
   Raportami wolnymi od zakresu są tylko pliki o dokładnych nazwach: `tasks/<id>/backend_r<n>.txt`, `audit_r<n>.txt`,
   `architect_review_r<n>.md`, `repo_before.hash`. Brak refu `main`/`master` = FAIL (bramka nie zgaduje bazy).
   Twarde reguły (FAIL): zakres, zamrożone pliki, ochrona `harness/` `.github/` `.githooks/`, składnia, ruff,
   twarde limity rozmiaru. Miękkie (WYMAGA_DECYZJI): próg rozmiaru, RATIO/TOTAL_LINES, poziom audytu.
   Rozmiar: kod 600 linii (twardo 900), testy 1200 (twardo 1800), funkcja 50 (twardo 80). Powyżej progu
   miękkiego CC pisze do BOARD.md jedno zdanie po co, a Owner akceptuje albo prosi o podział. Zasada nadal:
   nowa logika w nowym pliku — CC ma skłonność wpychać wszystko do jednego pliku, którego zależności potem
   sam nie widzi, a audytor też się w nim gubi.
5. **ARCHITECT_REVIEW** (sekcja 4) → BOARD.md.
6. Gdy **jednostka audytu** jest kompletna → audyt Codexa wg `AUDIT_TIER` (sekcja 5).
7. Owner mówi „zmerguj" → CC merguje do `main`, wypycha, **od razu usuwa branch** (zdalny i lokalny).

Jednostka audytu (`AUDIT_UNIT`) = logiczna całość, którą da się audytować razem (np. jeden pionowy
przekrój złożony z kilku Tasków). Domyślnie jeden Task = jedna jednostka. Dla wielu Tasków: każdy po
CONFORMS wpada na branch `unit/<nazwa>`, Codex audytuje jego head jednym przebiegiem, Owner merguje
`unit/<nazwa>` do `main`. Bramka `backend.py` biegnie dla KAŻDEGO Tasku osobno.

## 4. Architekt jako pierwszy audytor (decyzja Ownera 2026-09-21; CC popiera, z zabezpieczeniami)

**Po co:** architekt złapie błąd projektu i odejście od kontraktu wcześnie i tanio, zanim Codex wyda limit
na audyt; Codex audytuje raz, na gotową całość, zamiast wielu rund po drobiazgach. W Rocie błędy
„produktowe" (np. automat cofający decyzję człowieka) znajdował właśnie architekt, nie audytor mechaniczny.

**Czym jest ARCHITECT_REVIEW:** ocena zgodności dostarczonego SHA z kontraktem i minimalizmem. Wynik:
`CONFORMS` | `DEVIATIONS` (lista, każde z powołaniem na zdanie kontraktu) | `OWNER_DECISION_NEEDED`.
Zapis: `tasks/<id>/architect_review_r<n>.md` + wiersz w BOARD.md. Architekt **wpisuje wprost, czego nie
mógł sprawdzić** (nie uruchamia kodu).

**Czym NIE jest:** nie jest PASS kodu. Nie zastępuje audytu. Jedyny PASS/FAIL kodu wystawia audytor
niezależny od pisania i od projektu, na exact SHA. `CONFORMS` nie jest dowodem poprawności — audytor
buduje własny reproduktor i nie opiera się na opinii architekta.

**Zabezpieczenia (dlaczego to nie osłabia jakości):**
1. Architekt napisał kontrakt, więc dzieli jego założenia (ślepa plamka). Dlatego kod nadal sprawdza
   niezależny audytor — poza poziomem LIGHT.
2. Bramka mechaniczna biegnie na każdym Tasku niezależnie od opinii ludzi/modeli.
3. Duża paczka = późniejsze wykrycie błędu; łagodzą to: małe Taski, testy akceptacyjne CC per Task,
   ślad per commit (przy FAIL audytora szukamy Tasku, który go wprowadził).
4. Architekt nie dopisuje wymagań w trakcie review; propozycje idą osobno jako `ARCHITECTURE_PROPOSALS`.

## 5. Poziomy audytu (`AUDIT_TIER` w briefie)

Deklaruje architekt (brak = STANDARD). Audytor może tylko **podnieść**, ze wskazaniem powodu.
`harness/critical_paths.txt` daje mechaniczny wyzwalacz: zmiana pliku z tej listy przy niższym poziomie
w briefie = `WYMAGA_DECYZJI` z bramki.

| Poziom | Kiedy | ARCHITECT_REVIEW | Codex |
|---|---|---|---|
| **LIGHT** | dokumenty, teksty, konfiguracja bez logiki, małe zmiany bez zachowania | wymagane | niewymagany (Owner/architekt mogą wymusić) |
| **STANDARD** | zwykła funkcja z jednym szwem | wymagane | diff + reproduktory + testy zmienionego kodu + jeden realny przepływ |
| **CRITICAL** | trwałość, transakcje, skutki uboczne na zewnątrz, migracje, bezpieczeństwo, zmiana kontraktu | wymagane | jak STANDARD + niezależny reproduktor klasy błędu; pełna macierz tylko za zgodą Ownera |

Nazwy zgodne z narzędziem Maestro (`light/standard/critical`), żeby oba światy mówiły tym samym.
**Do potwierdzenia przez Ownera:** że LIGHT nie wymaga Codexa (oszczędność limitu). Zmiana na „zawsze
Codex" to jedna linia w tej tabeli i w `AGENTS.md`.

## 6. BOARD.md — jedno miejsce przekazań

Wszystko dla architekta/Codexa idzie do `BOARD.md`, nie przez Ownera. Statusy (dokładnie pięć):

| Status | Znaczy |
|---|---|
| `READY_FOR_ARCHITECT` | CC skończył Task, bramka PASS, czeka na ARCHITECT_REVIEW |
| `READY_FOR_CODEX` | jednostka audytu kompletna, wszystkie Taski CONFORMS |
| `CODEX_IN_PROGRESS` | audyt w toku |
| `CODEX_REPORTED` | raport gotowy pod wskazaną ścieżką |
| `OWNER_DECISION_NEEDED` | proces stanął na decyzji Ownera |

Zamknięty wiersz (merge/decyzja) usuwa ten, kto go zamyka — historia zostaje w `git log -p BOARD.md`.
Zawsze `git pull` przed edycją: architekt i Codex piszą tu równolegle. Rzeczy odłożone → `ODLOZONE.md`.

## 7. Mapa plików harnessu

| Plik | Rola |
|---|---|
| `harness/backend.py` | bramka mechaniczna (PASS/FAIL/WYMAGA_DECYZJI), mierzy dostarczony commit |
| `.github/workflows/gate.yml` | uruchamia bramkę automatycznie po pushu na `task/*` |
| `harness/guard.py` | blokada zamrożonych plików `harness/FROZEN.lock` |
| `harness/task_init.py` | start Tasku + zapis SHA bazowego + kontrola hooka |
| `harness/critical_paths.txt` | ścieżki wymuszające CRITICAL |
| `harness/templates/brief.md` | szablon briefu |
| `.githooks/pre-commit` | blokuje commit na `main`/`master` poza BOARD.md i ODLOZONE.md |
| `harness/tests/` | testy samego harnessu: `python -m pytest harness/tests` |
| `AGENTS.md`, `ARCHITECT_START_HERE.md`, `CLAUDE.md` | zasady per rola |

`harness/`, `.githooks/` i `.github/` są chronione: bramka odrzuca Task, którego zakres ich dotyka. Zmienia je
wyłącznie Owner/architekt, świadomym commitem.

## 8. Ochrona `main` (jednorazowo, robi Owner w ustawieniach repo)

Bez tego bramka jest tylko widoczna, nie wiążąca. Na publicznym repo jest to darmowe: Settings → Rules →
New branch ruleset → cel `main` → „Require status checks to pass" (`gate`) + „Block force pushes".
Uwaga: ruleset nie zna wyjątku „tylko BOARD.md", a dziś BOARD.md/ODLOZONE.md idą prosto na `main`. Do
rozstrzygnięcia z Ownerem: albo Owner ma bypass i tylko on pisze na `main`, albo BOARD.md też idzie
przez branch. Do czasu tej decyzji ruleset nie jest włączany.
