# RefCheck AI 🏀

**Basketball Coach Challenge Review Assistant**

Upload a charge/block clip — get an AI-powered verdict on whether the call should be upheld, overturned, or stand as called.

> RefCheck AI is designed to explain basketball calls, not replace referees.

---

## Problem Statement

Charge vs. blocking foul is one of the most controversial calls in basketball. Coaches challenge these calls frequently, but the rules around legal guarding position are nuanced and often misunderstood. RefCheck AI provides an AI-assisted breakdown of the play, comparing it to NBA/NCAA rule criteria.

## Why Charge vs. Block?

A working app that supports one review type well is better than a beautiful app that supports many poorly. Charge vs. block is:
- The most challenged call in basketball
- Based on clear visual criteria (feet set, body position, contact location)
- Well-suited for frame-by-frame video analysis

## Hackathon Requirements ✅

- ✅ Accepts short sports video
- ✅ Uses AI / multimodal analysis
- ✅ Compares play to rules
- ✅ Returns clear verdict
- ✅ Explains reasoning
- ✅ Supports basketball well
- ✅ Public GitHub repo
- ✅ Deploy ready

## Tech Stack

- **Frontend:** React + Vite
- **Backend:** Python FastAPI
- **Video Processing:** OpenCV
- **Analysis:** Mock AI / rule-based engine (multimodal AI ready)
- **Deploy:** Vercel (frontend) + Render/Railway (backend)

## Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`

## API Endpoints

### `GET /health`
Returns backend status.

### `GET /sample-cases`
Returns list of demo cases.

### `POST /review`
Multipart form: `original_call` (required), `sample_case_id` (optional), `file` (optional video upload).

Returns verdict, recommendation, confidence, evidence, rule reference, key frames, and limitations.

## Sample Cases

5 built-in demos work without video upload:
1. Clear Charge — Defender Set
2. Clear Blocking Foul — Defender Still Moving
3. No Call — Incidental Contact
4. Inconclusive — Bad Camera Angle
5. Close Call — Low Confidence

## AI Limitations

- MVP uses mock/rule-based analysis
- Camera angle and video quality affect accuracy
- Restricted area detection requires visible court lines
- Does not replace official referee judgment

## Deployment

### Frontend → Vercel

1. Push your repo to GitHub
2. Go to [vercel.com](https://vercel.com) and import the repo
3. Set the following:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Add environment variable:
   - `VITE_API_URL` = your deployed backend URL (e.g. `https://refcheck-api.onrender.com`)
5. Deploy

### Backend → Render

1. Go to [render.com](https://render.com) and create a new **Web Service**
2. Connect your GitHub repo
3. Set the following:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `MOCK_AI` = `true` (or `false` if you have OpenAI credits)
   - `OPENAI_API_KEY` = your key (only needed if `MOCK_AI=false`)
5. Deploy

### Backend → Railway (alternative)

1. Go to [railway.app](https://railway.app) and create a new project from GitHub
2. Set **Root Directory** to `backend`
3. Railway auto-detects Python — add a `Procfile` if needed:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Add the same environment variables as above
5. Deploy

### Post-Deploy CORS

After deploying, add your Vercel frontend URL to the CORS origins in `backend/app/main.py`:

```python
allow_origins=[
    "http://localhost:5173",
    "https://your-app.vercel.app",  # add this
]
```

## Future Work

- Integrate real multimodal vision model (GPT-4o / Gemini)
- Train on labeled basketball officiating clips
- Add pose estimation for body position analysis
- Detect restricted area arc from court lines
- Add more review types (shooting foul, goaltending, etc.)

---

*Built for BorderHack '26 — Track 02 Sports Officiating Analysis*
