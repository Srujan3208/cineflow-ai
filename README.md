# CineFlow AI — Prompt to Video

Responsive prompt-to-video frontend with a Python rendering worker.

## Frontend
- Static app in `web/index.html`
- Vercel deployment: repository root, output directory `web`, no build command

## Backend
The Flask worker in `worker/` runs long video-rendering jobs and must be deployed to a persistent container host (Render/Railway or equivalent), not Vercel serverless.

## Current status
The frontend source and Vercel configuration are committed. Backend source is still being uploaded. The UI currently requires a running worker at the same origin or a configured API base URL before generation can work.

## Project files
- `web/`: web interface
- `worker/`: rendering API and video pipeline
- `supabase/migrations/`: planned generation history and storage schema
- `docs/DEPLOYMENT.md`: deployment instructions
