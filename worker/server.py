"""CineFlow render worker API. Keep this process on a persistent worker, not Vercel serverless."""
import os, pathlib, threading, time, uuid
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
import pipeline, storyboard as sbmod

HERE = pathlib.Path(__file__).parent.resolve()
JOBS_DIR = pathlib.Path(os.environ.get("JOBS_DIR", HERE / "jobs")).resolve()
JOBS_DIR.mkdir(parents=True, exist_ok=True)
WEB_DIR = pathlib.Path(os.environ.get("WEB_DIR", HERE.parent / "web")).resolve()
app = Flask(__name__)
CORS(app, origins=os.environ.get("ALLOWED_ORIGINS", "*").split(","))
pool = ThreadPoolExecutor(max_workers=1)
jobs = {}
lock = threading.Lock()

def work(jid, prompt, size):
    job = jobs[jid]
    def progress(pct, msg):
        with lock:
            if pct is not None: job["progress"] = pct
            job["log"].append(str(msg)[-400:])
            job["log"] = job["log"][-60:]
    try:
        job["status"] = "running"
        progress(3, "Writing storyboard")
        sb = sbmod.make_storyboard(prompt)
        job["storyboard"] = sb
        progress(10, "Storyboard ready: " + sb["title"])
        job["file"] = str(pipeline.build(JOBS_DIR / jid, sb, progress, size))
        job["status"] = "done"
    except Exception as exc:
        job["status"], job["error"] = "error", str(exc)[-900:]

@app.get("/health")
def health(): return jsonify(status="ok", service="cineflow-render-worker")

@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not 3 <= len(prompt) <= 800: return jsonify(error="Write a prompt between 3 and 800 characters."), 400
    size = data.get("size") if data.get("size") in ("720x1280", "1080x1920") else "720x1280"
    jid = uuid.uuid4().hex[:12]
    folder = JOBS_DIR / jid; folder.mkdir(parents=True, exist_ok=False)
    jobs[jid] = {"id": jid, "status": "queued", "progress": 0, "log": ["Queued"], "created": time.time(), "prompt": prompt}
    pool.submit(work, jid, prompt, size)
    return jsonify(id=jid, status="queued")

@app.get("/api/jobs/<jid>")
def status(jid):
    j = jobs.get(jid)
    if not j: return jsonify(error="Unknown or expired job"), 404
    result = {k:v for k,v in j.items() if k != "file"}
    result["video"] = f"/api/video/{jid}" if j["status"] == "done" else None
    return jsonify(result)

@app.get("/api/video/<jid>")
def video(jid):
    j = jobs.get(jid)
    if not j or j.get("status") != "done" or not pathlib.Path(j.get("file", "")).is_file():
        return jsonify(error="Video is not ready"), 404
    return send_file(j["file"], mimetype="video/mp4", conditional=True, download_name=f"cineflow-{jid}.mp4")

@app.get("/")
def index(): return send_from_directory(WEB_DIR, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), threaded=True)
