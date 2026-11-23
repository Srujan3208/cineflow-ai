# CineFlow AI

Prompt-to-video generation web application.

## Architecture

- Frontend: responsive chat-style web UI
- API/worker: Python Flask video generation worker
- Video rendering: cinematic motion graphics pipeline with FFmpeg
- Database and storage: Supabase (planned integration)
- Frontend deployment: Vercel
- Worker deployment: persistent container service (required for rendering)

## Project package

The complete project package is prepared separately as `cineflow-ai-project.zip` in the development workspace. The source files still need to be uploaded to this repository before Vercel can deploy the full application.

## Deployment notes

Vercel is intended for the frontend. The Python rendering worker must run on a persistent service/container. Configure the frontend API base URL to the worker's deployed URL.

See `docs/DEPLOYMENT.md` once source files are uploaded.
