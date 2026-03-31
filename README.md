# TOQP Backend — The Order of the Quiet Path

API backend voor spirituele chart berekeningen: Human Design, BaZi, Numerologie.

## Endpoints

| Method | URL | Beschrijving |
|--------|-----|-------------|
| GET | `/` | Health check |
| POST | `/api/numerology` | Numerologie berekening |
| POST | `/api/bazi` | BaZi Vier Pilaren |
| POST | `/api/human-design` | Human Design chart |
| POST | `/api/reading` | Gecombineerde reading tekst |

## Request formaat

Alle POST endpoints accepteren JSON:

```json
{
  "firstname": "Timo",
  "lastname":  "Reets",
  "day":    15,
  "month":  6,
  "year":   1990,
  "hour":   14,
  "minute": 30,
  "lat":    51.05,
  "lon":    3.72,
  "tz":     2
}
```

## Lokaal draaien

```bash
npm install
npm run dev
```

API draait op http://localhost:3000

## Deploy op Render

1. Push deze repo naar GitHub
2. Ga naar render.com → New Web Service
3. Koppel je GitHub repo
4. Render detecteert automatisch de `render.yaml`
5. Deploy → je krijgt een URL zoals `https://toqp-backend.onrender.com`
6. Vervang in je frontend: `const API = "https://jouw-url.onrender.com"`
