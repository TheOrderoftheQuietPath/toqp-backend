# TOQP Backend — The Order of the Quiet Path

Python/Flask backend voor de spirituele calculators van [theorderofthequietpath.github.io](https://theorderofthequietpath.github.io)

## Endpoints

### POST /api/bazi
BaZi — Vier Pilaren van Lot calculator.

```json
{
  "year": 1989, "month": 5, "day": 31,
  "hour": 20, "minute": 20,
  "lon": 4.45, "tz": 2,
  "gender": "M"
}
```

Geeft: 4 pilaren, dag-meester analyse, vijf factoren, verborgen stammen,
Shen Sha sterren, gelukspilaren, jaar-interactie 2026.

### POST /api/human-design
Human Design bodygraph calculator.

```json
{
  "year": 1989, "month": 5, "day": 31,
  "hour": 20, "minute": 20, "tz": 2
}
```

Geeft: type, autoriteit, profiel, definitie, incarnatiekruis, variabelen/4 pijlen,
64 poorten (met I Ching namen, keynotes, schaduw, gave), 36 kanalen (met circuits),
centrum definities, gelukssterren.

### POST /api/numerology
Numerologie calculator.

```json
{
  "year": 1989, "month": 5, "day": 31,
  "firstname": "Timothy", "lastname": "Raeymaekers"
}
```

Geeft: levenspad, zielsverlangen, persoonlijkheid, lot, verjaardag.

### POST /api/reading
Gecombineerde verhalende reading (HD + BaZi + Numerologie).

## Technisch

- Python 3.11 / Flask
- Swiss Ephemeris (pyswisseph) voor astronomische berekeningen
- Gedeployed op Render.com

## Accuraatheid BaZi

- ✅ Jaarpilaar via exacte Li Chun (315° zon, ~4 feb)
- ✅ Maandpilaar via exacte Solar Terms (30° stappen)
- ✅ Dagpilaar via Flowtastic-compatibele epoch (offset 49)
- ✅ Uurpilaar via lokale kloktijd (conform Flowtastic/Saju standaard)
- ✅ Zomertijd auto-detectie voor België/Nederland
- ✅ Early Zi correctie (geboorte 23:00-01:00)

## Accuraatheid Human Design

- ✅ Design moment: 88° zon vóór geboorte (binaire zoekopdracht)
- ✅ Swiss Ephemeris voor alle planeetposities
- ✅ Correcte kanaal-gebaseerde centrum definitie
- ✅ Autoriteit berekening (Solar/Sacral/Spleen/Ego/Zelf-geprojecteerd/Mentaal/Lunair)
- ✅ Variabelen / 4 pijlen (Determinatie/Omgeving/Motivatie/Perspectief)
