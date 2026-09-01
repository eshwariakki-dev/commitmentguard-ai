# CommitmentGuard AI

A self-correcting trust layer for agentic commerce. Verifies that a merchant
can actually fulfill what an AI shopping agent proposes — stock, price, and
delivery — before checkout. If a proposed product fails, it automatically
finds and re-verifies the nearest fulfillable alternative.

## How it works

1. Buyer types a request in plain English (e.g. "headphones under ₹3000, delivered tomorrow")
2. `nlp_parser.py` extracts structured requirements (category, budget, delivery window) — uses Gemini if `GEMINI_API_KEY` is set, otherwise a deterministic fallback parser (works with zero setup)
3. `commitment_guard.py` — pure deterministic Python, no AI — checks the proposed product against real catalog data
4. If it fails any check, the same engine searches for the nearest product that passes all checks, and re-verifies it
5. Every step is logged to an audit trail returned to the frontend

**Key architectural point:** the AI only interprets buyer language. It never
decides whether a product is actually deliverable — that decision is 100%
deterministic Python logic reading real data from `products.json`. This
separation is the whole point of the project — an AI agent should never be
the one certifying its own promises.

## Project structure

```
commitmentguard-ai/
  backend/
    app.py               Flask server, exposes POST /api/verify
    commitment_guard.py   Verification + self-correction engine (no AI)
    nlp_parser.py         Natural language -> structured requirements
    products.json         Merchant catalog (10 products)
    requirements.txt
  frontend/
    src/
      App.jsx             Main dashboard
      components/         RequirementsCard, VerificationCard, AlternativeCard, AuditTrail
```

## Running it — step by step

You need two terminals open at the same time: one for the backend, one for the frontend.

### Terminal 1 — Backend

```bash
cd commitmentguard-ai/backend
pip install -r requirements.txt
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

Leave this terminal running. Don't close it.

**Note on Gemini (optional):** the app works with zero configuration using the
fallback parser. If you want real Gemini-powered language understanding,
get a free API key at https://aistudio.google.com/apikey and set it before
running the backend:

```bash
# Mac/Linux
export GEMINI_API_KEY=your_key_here

# Windows (cmd)
set GEMINI_API_KEY=your_key_here
```

Then run `python app.py` again.

### Terminal 2 — Frontend

Open a **new** terminal window (leave the backend one running), then:

```bash
cd commitmentguard-ai/frontend
npm install
npm run dev
```

You should see:
```
  VITE  ready in ... ms
  ➜  Local:   http://localhost:5173/
```

Open that link in your browser. You should see the CommitmentGuard AI dashboard.

## Demo script (for judges)

Type this exact request and click "Verify Request":

> I need wireless headphones under ₹3000 delivered tomorrow

Walk through what happens on screen:
1. **AI understanding** — shows the extracted category, budget, delivery window
2. **Commitment verification** — proposes SoundWave Pro Headphones (₹2799). Passes stock and budget, **fails delivery** (3-day, not 1-day) — shown as BLOCKED with the exact reason
3. **Self-correction** — automatically finds AirFit Sport Headphones (₹2899), re-verifies it against all three checks, shows VERIFIED
4. **Audit trail** — full timestamped log of every decision the system made, in order

Other requests to try:
- `Looking for a wallet under 1500` — clean VERIFIED, no correction needed
- `I need headphones under 800` — no product fits, so it should return NO_MATCH or NO_ALTERNATIVE, demonstrating the system refuses to fabricate a fake promise

## Troubleshooting

- **"Cannot reach the backend" error in the browser:** make sure Terminal 1 (Flask) is still running and shows port 5000.
- **`pip install` fails:** try `pip3` instead of `pip`, or `python3 app.py` instead of `python app.py`.
- **Port 5000 already in use:** close whatever else is using it, or change the port number in `app.py`'s last line and update `API_BASE` in `frontend/src/App.jsx` to match.
