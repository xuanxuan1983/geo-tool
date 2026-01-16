# GEO Tool – Streamlit Web UI

## Overview
A lightweight **Streamlit** web interface that wraps the existing GEO pipeline (`run_full_pipeline.py`, `ai_pressure_test_multi.py`, `generate_comparison_report.py`).

- **Roles**: Admin (full access) / Team Member (run pipeline, view results).
- **Features**:
  - One‑click D→B→C→A execution.
  - Multi‑engine AI pressure testing.
  - Before/After comparison reports.
  - Secure password‑based login (hashes stored in `.env`).
  - Dockerized deployment (Dockerfile + `docker‑compose.yml`).

## Quick Start (Local)
```bash
# 1. Clone repo (already in your workspace)
cd /Users/xuan/Documents/write\ agent/geo_business_tool

# 2. Create a virtual env & install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Set passwords (replace placeholders in .env)
#   Generate SHA‑256 hash:
#   python -c "import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())"
#   Paste the hash into ADMIN_PASSWORD_HASH / MEMBER_PASSWORD_HASH

# 4. Run the app
streamlit run scripts/app.py
```
Open `http://localhost:8501` in a browser.

## Docker Deployment
```bash
# Build and run the container
docker compose up --build -d
```
The app will be reachable at `http://localhost:8501`. The `output/` directory is mounted as a volume, so all generated files persist on the host.

## Environment Variables (`.env`)
| Variable | Purpose |
|----------|---------|
| ADMIN_PASSWORD_HASH | SHA‑256 hash of the admin password |
| MEMBER_PASSWORD_HASH | SHA‑256 hash of the member password |
| DEEPSEEK_API_KEY | Your DeepSeek API key (already in `config.py`) |
| OPENAI_API_KEY | API key for ChatGPT (optional) |

## File Structure
```
geo_business_tool/
├─ scripts/
│   ├─ app.py          # Streamlit UI
│   ├─ auth.py         # Login & role handling
│   ├─ wrapper.py      # Calls existing pipeline scripts
│   ├─ run_full_pipeline.py
│   ├─ ai_pressure_test_multi.py
│   └─ generate_comparison_report.py
├─ output/            # Generated client files (mounted in Docker)
├─ .env               # Secrets (do NOT commit)
├─ Dockerfile
├─ docker-compose.yml
└─ README.md
```

## Next Steps
- Replace the placeholder password hashes in `.env`.
- (Optional) Add Feishu OAuth in `auth.py`.
- Customize branding: replace the DMY logo path in `app.py`.

---
*Feel free to open an issue or PR if you need further tweaks.*
