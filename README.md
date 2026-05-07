<<<<<<< HEAD
# NyayaSetu v2.0 — AI Legal Assistant
### Production-Grade · Demo-Day Ready · Hackathon Winning

---

## Project Structure

```
nyayasetu/
├── app.py                    ← Flask entry point
├── requirements.txt
├── Dockerfile
├── .env.example
├── config/
│   ├── __init__.py
│   └── settings.py           ← All config in one place
├── routes/
│   ├── __init__.py
│   ├── chat.py               ← POST /chat
│   └── api.py                ← POST /api/check, /api/letter
├── services/
│   ├── __init__.py
│   ├── ai_service.py         ← Gemini + retry + fallback
│   └── fallback.py           ← Intelligent demo responses
└── frontend/
    └── index.html            ← Complete UI (chat + welfare)
```

---

## Run Locally — 3 Commands

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set API key
export GEMINI_API_KEY=your_key_here    # Mac/Linux
set GEMINI_API_KEY=your_key_here       # Windows

# 3. Run
python app.py
```
Open: **http://localhost:8080**

---

## What's New in v2.0

| Feature | Details |
|---|---|
| **Retry System** | 3 retries with exponential backoff on 429 |
| **Demo Mode** | App never crashes — intelligent fallbacks always work |
| **Chat Interface** | ChatGPT-style with structured legal responses |
| **Structured Responses** | Legal Context → Your Rights → Action → Note |
| **Model Switching** | gemini-2.0-flash → fallback if fails |
| **Global Error Handling** | No endpoint ever crashes |
| **Production Logging** | All requests, errors, AI responses logged |
| **Clean Architecture** | routes / services / config separated |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Frontend UI |
| GET | /health | System status + AI mode |
| POST | /chat | Legal chat (with history) |
| POST | /api/check | Welfare eligibility check |
| POST | /api/letter | Generate application letter |

---

## Demo Inputs

### Chat Test
```
"My employer hasn't paid my salary for 3 months"
"Police refused to file my FIR"
"I am facing domestic violence"
"How do I file an RTI?"
```

### Welfare Check
```
Age: 35, Female, Maharashtra, Farmer, Below ₹10,000, OBC
Age: 42, Male, UP, Daily Wage Labourer, Below ₹10,000, SC
Age: 28, Male, Delhi, Street Vendor, ₹10k-25k, General
```

---

## Cloud Run Deploy

```bash
# Build
gcloud builds submit --tag gcr.io/YOUR_PROJECT/nyayasetu .

# Deploy
gcloud run deploy nyayasetu \
  --image gcr.io/YOUR_PROJECT/nyayasetu \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=YOUR_KEY \
  --memory 512Mi \
  --port 8080
```

---

## Fix Common Errors

| Error | Fix |
|---|---|
| `429 quota exceeded` | App auto-switches to demo mode — no action needed |
| `404 model not found` | Already using gemini-2.0-flash in config |
| `Port already in use` | Change PORT in .env to 8081 |
| `Module not found` | Run `pip install -r requirements.txt` again |
| `Service Unavailable` | Check GEMINI_API_KEY is set correctly |
=======
# Nyayasetu
AI-powered legal-tech platform that simplifies government schemes, legal procedures, and citizen assistance through intelligent guidance and multilingual support.
>>>>>>> 1076564be0994ae2155b278e1144e3049a3165e4
