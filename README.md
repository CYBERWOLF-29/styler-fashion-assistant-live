# STYLER

STYLER is a modular Streamlit-based personal fashion assistant that helps users decide what to wear using their own wardrobe, personal colour profile, and occasion context.

## Features
- JARVIS-inspired voice-first style assistant experience
- Digital wardrobe capture and categorisation
- Personal colour profiling with an emphasis on user confirmation
- Outfit recommendation engine that respects the user's wardrobe only
- Browser voice mode: start listening, say “Hey STYLER,” then ask for an outfit; responses can be spoken aloud
- Saved outfits, history, and personal preferences
- Responsive desktop and mobile web interface

## Run locally
1. Create and activate a virtual environment.
2. Install dependencies:
   python -m pip install -r requirements.txt
3. Start the app:
   streamlit run app.py

## Deploy a public demo on Streamlit Community Cloud
1. Push this project to a public GitHub repository. Do not include `.env`, `.streamlit/secrets.toml`, or `data/*.json`.
2. Create a new app at [share.streamlit.io](https://share.streamlit.io) from that repository and set the main file to `app.py`.
3. In the app's **Settings → Secrets**, add:
   ```toml
   STYLER_DEMO_MODE = "true"
   ```
4. Deploy. The demo starts with a clean profile and keeps changes only in the current Streamlit browser session. Shared local-file persistence is disabled.

The public demo is for sample data only. It has no account authentication or private database, so do not enter sensitive personal information. For durable per-user wardrobes and photo storage, integrate Supabase authentication, row-level security, and private storage before enabling persistent multi-user use.

## Environment variables
Copy `.env.example` to `.env` and add your secrets before integrating remote AI providers.

## Architecture
The project is organised into a modular layout for UI, services, database access, and styling logic.

## Notes
- No API keys are committed to source control.
- AI analysis should be treated as assistive and always confirmed by the user when a recommendation matters.
- Voice mode requires microphone permission and a supported browser (Chrome or Edge recommended). Listening is active only after the user starts it and while the app tab remains open. Browser speech-recognition providers may process audio; the app does not provide an always-on or locked-phone wake word.
- If browser speech recognition is unavailable or denied, the “Or type a command” field remains available.
- `STYLER_DEMO_MODE=true` (or the matching Streamlit secret) disables shared local JSON persistence for public demos.
