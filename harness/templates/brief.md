# <TASK_ID> — <krótka nazwa>

Status: DRAFT (zmień na FROZEN z datą, gdy Owner zaakceptuje; potem brief się nie zmienia)
AUDIT_TIER: STANDARD
MAX_NEW_FILES: 2
TOTAL_LINES_THRESHOLD: 150
AUDIT_UNIT: <nazwa całości, jeśli Task jest częścią większej jednostki audytu; inaczej usuń tę linię>

<!-- Pola nagłówka (od pierwszej kolumny, bez spacji): AUDIT_TIER = LIGHT|STANDARD|CRITICAL, dokładnie raz.
     MAX_NEW_FILES i TOTAL_LINES_THRESHOLD opcjonalne (domyślnie 2 i 150), liczby 1-1000. Czyta je harness/backend.py. -->

## Cel (zachowanie widoczne dla Ownera, prostym językiem)

## Decyzje Ownera (zamrożone)

## Zakres

TASK_SCOPE:
- app/**
- tests/test_<x>.py

<!-- Wpisy: dokładne pliki albo katalogi z ** lub * (np. app/**, tests/*.py). Pierwszy segment dosłowny.
     Bez harness/, .githooks/, ścieżek bezwzględnych i "..". Wymień tyle, ile Task naprawdę potrzebuje. -->

## READ_ONLY_EVIDENCE
Pliki, które implementer może tylko czytać (np. zamrożony spec).

## OUT_OF_SCOPE
Czego nie wolno ruszać ani dokładać.

## Testy akceptacyjne

## Definicja PASS

## Wyjście z zakresu
Jeśli do poprawnej realizacji potrzebny jest plik spoza TASK_SCOPE: implementer ZATRZYMUJE się i pyta
(BOARD.md), pokazując konkretny powód i odrzuconą alternatywę. Nigdy nie poszerza zakresu sam.
