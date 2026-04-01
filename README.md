# TOQP Backend — Python (pyswisseph)

100% accurate spiritual chart calculations using Swiss Ephemeris.

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Health check |
| POST | `/api/human-design` | HD chart (pyswisseph) |
| POST | `/api/bazi` | BaZi Four Pillars |
| POST | `/api/numerology` | Numerology |
| POST | `/api/reading` | Combined reading text |

## Request

```json
{
  "firstname": "Timo",
  "lastname": "Reavan",
  "day": 31, "month": 5, "year": 1989,
  "hour": 20, "minute": 20,
  "lat": 51.15, "lon": 4.45, "tz": 2
}
```

## Deploy on Render

1. Push to GitHub repo `toqp-backend`
2. On Render: delete existing Node.js service OR update settings:
   - **Language**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
3. Deploy → pyswisseph compiles automatically on Render's Linux
4. Logs will show: `TOQP API running` when ready

## Local testing

```bash
pip install -r requirements.txt
python app.py
```
