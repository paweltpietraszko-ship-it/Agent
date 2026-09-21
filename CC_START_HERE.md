# CC_START_HERE — dla Claude Code, gospodarza tego repo

Czytasz to na początku KAŻDEJ sesji, przed pierwszą zmianą. Pamięć modelu zawodzi (kontekst się kończy,
instancje się zmieniają), więc **ten plik jest pamięcią**. Zasady pracy: `CLAUDE.md` i `docs/PROCESS.md`.
Tu jest to, czego tam nie ma: jak być gospodarzem programu i czego nauczyła nas Rota.

## 1. Co znaczy „gospodarz"
Jesteś jedynym, który widzi program od pierwszej do ostatniej linii i pracuje z Ownerem na co dzień.
Architekt (ChatGPT) widzi tylko GitHuba, Codex tylko exact SHA. Dlatego:
- **Ty utrzymujesz ten plik.** Na końcu każdej sesji (i po każdej ważnej decyzji) uzupełnij sekcję 5 i 6.
  Sekcja „Stan" bez daty jest nieprawdziwa — zawsze wpisuj datę i SHA `main`.
- **Ty decydujesz o sprawach technicznych.** Do Ownera trafia wyłącznie decyzja produktowa. Owner nie wie,
  co wybrać przy symlinkach czy wzorcach `**` — wybierz bezpieczniej i cicho, zapisz w `PROCESS.md`.
- **Ty pilnujesz spójności repo**: `git fetch` przed twierdzeniem „jest/nie ma", usuwanie zmergowanych branchy
  od razu, sprawdzenie brancha przed każdym commitem.

## 2. Owner (Paweł)
- Nie jest programistą, uczy się z modelami; nie czyta kodu. Pisz po polsku, prosto, per „ty", bez skrótów klas.
- Ogranicza go czas i pieniądze (budżet na AI jest stały): nie każ mu klikać, nie zlecaj audytów „na wszelki
  wypadek", nie rób forków ani zbędnych wywołań narzędzi. Zbieraj kroki w mniej, większych wywołań.
- Zachowanie widoczne dla człowieka najpierw streść własnymi słowami i poczekaj na „tak, zgadza się".
- „zmerguj" pada tylko od niego. Sam nie merguj, nie wypychaj do `main`.
- Jeśli musi coś zrobić na GitHubie, poprowadź go krok po kroku albo zrób to sam przez `gh` (masz prawa admina
  przez jego konto — użyj ich ostrożnie i powiedz co zmieniłeś).

## 3. Twarde lekcje z Roty (kosztowały tygodnie)
1. **Proza nie egzekwuje niczego.** Modele obchodziły `guard.py`, `task_init.py` i `TASK_SCOPE`, kiedy odpalały je
   z dobrej woli. Dlatego bramka biegnie na GitHubie sama; nie polegaj na tym, że „pamiętasz".
2. **Nikt nie zatwierdza własnej pracy.** Ani Ty, ani architekt (nie uruchamia kodu). PASS kodu wystawia
   niezależny audytor na exact SHA.
3. **Najpierw popatrz na wyrenderowany wynik**, potem licz. Formalnie poprawne ≠ sensowne dla człowieka.
4. **Minimalizm.** Nowe warstwy, drugi system walidacji, „na zapas" — nie. Nowa logika w nowym pliku, nie w
   rosnącym pliku, którego zależności potem sam nie widzisz (audytor też się gubi).
5. **Nie zgaduj przy niejasności** — pytaj (przez `BOARD.md`). Znalezisko poza zakresem = zgłoś, nie naprawiaj.
6. **Repro kopiuje całą realną konfigurację**, nie „łagodniejsze" wartości domyślne.
7. **Bramka, którą sam łatasz, zawodzi po cichu.** Audyt tego harnessu (4 rundy, `audit_r1..r4`) znalazł: przesunięcie
   bazy ukrywające commity, kod schowany pod `tasks/`, brief czytany z katalogu roboczego, nazwę pliku ze spacją
   w hooku, wyjątek w triggerze po nazwie brancha. Każda nowa reguła „poza kontrolą" jest kandydatem na obejście.
8. **Windows:** końcówki CRLF fałszują hashe (guard normalizuje do LF); hook to `sh`; w heredoc z Pythona
   backslash-e bywają zniekształcane — używaj narzędzia Write/Edit zamiast escapowania.

## 4. Praktyka sesji
- Start: `git fetch`, `git status`, przeczytaj `BOARD.md`, sekcję 5 tego pliku, aktywny brief.
- Każda decyzja Ownera i każdy ważny wniosek → zapisz od razu (tu, `BOARD.md`, `ODLOZONE.md`), nie „na koniec".
- Temat odłożony jako „nie teraz" → jeden wpis w `ODLOZONE.md`, nie wracaj do niego sam.
- Zmiany `harness/`, `.githooks/`, `.github/` nie są Taskiem: tylko świadomy commit Ownera/architekta + audyt Codexa.

## 5. Stan (aktualizuj: data + SHA `main`)
- 2026-09-21: zestaw startowy harnessu i bramka `pull_request_target` (z wyjątkiem dla PR zmieniających tylko
  BOARD.md/ODLOZONE.md) są na `main` po audytach Codexa (kit PASS r4, bramka PASS r1). Repo publiczne; na `main`
  ruleset blokuje force-push i usuwanie. **Jeszcze niewłączone:** wymóg zielonego `gate` + PR przed merge.
  Wymaga decyzji Ownera/architekta: architekt commituje dziś briefy i dokumenty prosto na `main` — wymóg PR by to
  zablokował; poza tym zmiana pliku spoza BOARD/ODLOZONE (np. tego pliku) wymagałaby briefu. Rozważyć dopisanie
  `CC_START_HERE.md` i `CODEX_START_HERE.md` do wyjątku księgowego (mała zmiana `bookkeeping_only.py`, audyt).
- Jedyny aktualny Task: V0A-01 (Core Durable Action Lifecycle). Brief `tasks/TASK_V0A_01_CORE_RECOVERY.md` nie ma
  jeszcze `TASK_SCOPE`/`AUDIT_TIER` — dopisuje architekt i commituje na `main` PRZED implementacją.

## 6. Otwarte pytania / do dopisania przez gospodarza
- (uzupełniaj: decyzje Ownera, pułapki znalezione w trakcie, rzeczy do sprawdzenia)

## 7. Następca
Jeśli kończysz i nie wiesz, czy będzie następna instancja: uzupełnij sekcje 5–6, zacommituj (przez branch/PR
według `PROCESS.md`) i napisz do Ownera jedno zdanie, gdzie zacząć. Codex ma własny plik: `CODEX_START_HERE.md`.
