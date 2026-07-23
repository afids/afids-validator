# AFIDs Validator — Deploy Handoff: AI Tutor (`/learn`) + Groq

**Goal:** deploy the new **AI-tutor branch** to the live site **https://validator.afids.io**, with the guided-learning tutor (`/learn`) backed by a shared Groq API key so any visitor can use it without their own key.

**Who this is for:** whoever currently has **SSH/admin access to the production server**. The code and the app-layer wiring are done and tested; the only remaining work is server-side deployment, which requires access this document's author does not have.

---

## 1. What's being deployed

- **Repo:** `github.com/afids/afids-validator`
- **Branch:** `enh/ai-tutor-learning-mode` (open PR **#253** → `master`, 17 commits ahead, mergeable)
- **What it adds:**
  - `/learn` guided-learning AI tutor (`afidsvalidator/learn.py`, `llm.py`, `templates/learn.html`)
  - One **additive**, non-destructive DB migration: a `knowledge_chunks` table (`migrations/versions/c4e7f1a9b2d8_.py`)
  - Macaque templates + reliability-calibration features
- **Status:** code complete and pushed; tutor→Groq path tested locally and works (streams live Llama 3.3 70B). Nothing is deployed to production yet — `/learn` currently 404s on the live site.

> **Note on CI:** PR #253's checks show red only because the repo uses `pull_request_target`, which runs the workflow definition from `master` (still has an old Python 3.8 matrix). This does **not** affect the deploy — the deploy workflow is manual (`workflow_dispatch`) and runs on whatever branch you point it at. You do **not** need CI green or a merge to deploy.

---

## 2. How production deploys work (important — not Docker)

The live site is **not** run via `docker compose` (that's local-dev only). Production is a **wheel + venv + systemd** setup, deployed by a GitHub Actions workflow (`.github/workflows/deploy.yml`) that SSHes into the server. On trigger it:

1. Builds a Python wheel from the chosen branch (`poetry build`).
2. Writes a production `.env` from **GitHub Actions Secrets**.
3. Runs `fabrictasks.py`, which SSHes into the server and:
   - copies the wheel + `.env` into `/opt/afidsvalidator/releases/afidsvalidator-<timestamp>/`
   - flips the `/opt/afidsvalidator/current` symlink to the new release
   - `pip install <wheel>[deploy]` into `/opt/afidsvalidator/venv-afidsvalidator`
   - runs `flask db upgrade` (applies the migration)
   - `sudo systemctl restart afidsvalidator.service`

So a deploy = **build wheel → ship over SSH → migrate DB → restart service.**

---

## 3. Prerequisites on the production server

Confirm these are true on the live box before deploying:

- [ ] SSH reachable; the deploy user's `~/.ssh/authorized_keys` contains the public key whose private half will be stored as the `PRIVATE_KEY` secret (see §4).
- [ ] Directory layout exists: `/opt/afidsvalidator/releases/` and venv `/opt/afidsvalidator/venv-afidsvalidator/`.
- [ ] **Passwordless sudo** for the deploy user (the workflow runs `sudo systemctl restart afidsvalidator.service`; it will hang on a password prompt).
- [ ] `afidsvalidator.service` systemd unit exists and serves the app from the `current` symlink (already true — the site serves today).
- [ ] Postgres running and reachable at the `DATABASE_URL` you'll put in the secrets.

Quick verification commands (run on the box / from your machine):

```bash
ls -ld /opt/afidsvalidator/releases /opt/afidsvalidator/venv-afidsvalidator
/opt/afidsvalidator/venv-afidsvalidator/bin/python --version      # note this version (see gotcha in §6)
sudo -n systemctl status afidsvalidator.service >/dev/null && echo "passwordless sudo OK"
ssh -i <your_private_key> <deploy_user>@<host> 'echo connected'
```

---

## 4. GitHub Actions Secrets

Set these on the repo (Settings → Secrets and variables → Actions, or the `gh secret set` commands below). **Secret values are entered at a hidden prompt or read from a file — never inline, never committed.**

| Secret | What it is | Likely action |
|---|---|---|
| `PRODUCTION_URL` | SSH deploy target `user@host` (e.g. `ubuntu@<ip>`) | **Update** — current value is from 2023 and points at a decommissioned server. |
| `PRIVATE_KEY` | SSH **private** key whose public half is in the box's `authorized_keys` | **Update** — must be a key the current box trusts. |
| `PRODUCTION_DATABASE_URL` | Postgres connection string on the live box | **Verify** it matches the current box (see ⚠️ in §6). |
| `PRODUCTION_SECRET_KEY` | Flask session secret | **Verify** it matches the current box. |
| `PRODUCTION_FLASK_ENV` | e.g. `production` | Verify. |
| `PRODUCTION_ORCID_OAUTH_CLIENT_ID` / `_SECRET` | ORCID login creds | Verify (only affects user login). |
| `PRODUCTION_LLM_API_KEY` | **Groq API key** for the shared tutor | **Already set.** Optionally replace with a production-only key so it can be rotated independently of local dev. |

The tutor's provider URL/model are **not** secrets — `deploy.yml` defaults them to Groq's Llama 3.3 70B (`https://api.groq.com/openai/v1`, `llama-3.3-70b-versatile`). The deploy is fail-safe: if `PRODUCTION_LLM_API_KEY` is empty, the LLM vars simply aren't written and the tutor falls back to static reference text instead of erroring.

Commands (run from a clone of the repo):

```bash
gh secret set PRODUCTION_URL                       # paste user@host at prompt
gh secret set PRIVATE_KEY < /path/to/deploy_private_key
# only if the 2023 values no longer match the current box:
gh secret set PRODUCTION_DATABASE_URL
gh secret set PRODUCTION_SECRET_KEY
# to use a prod-specific Groq key (optional):
gh secret set PRODUCTION_LLM_API_KEY               # paste gsk_... at prompt

gh secret list                                     # confirm names + timestamps
```

To get a free Groq key (if you'd rather use your own): https://console.groq.com/keys — free tier, no credit card. It only needs read access to chat models.

---

## 5. Deploy and verify

```bash
# Trigger against the tutor branch (or 'master' if you merge #253 first)
gh workflow run "AFIDs Validator Deploy" --ref enh/ai-tutor-learning-mode

# Watch — the make-or-break step is "Deploy release" (the SSH step)
gh run watch $(gh run list --workflow=deploy.yml --limit 1 --json databaseId -q '.[0].databaseId')
```

Verify on the live site:

- [ ] `https://validator.afids.io/learn` loads (no 404).
- [ ] The tutor returns a **live streamed** response (confirms the Groq key landed) — not just static text.
- [ ] A normal FCSV upload still validates (confirms the migration + restart were clean).

---

## 6. Gotchas (please read)

1. **⚠️ Stale secrets can break a "successful" deploy.** The deploy **overwrites** the server `.env` from the GitHub Secrets. Most non-LLM secrets were set in **2023** (before the server was re-hosted). If `PRODUCTION_DATABASE_URL` / `PRODUCTION_SECRET_KEY` no longer match the current box, the deploy will run "green" but leave the site pointing at the wrong DB / invalidate sessions. **Before deploying, read the current `/opt/afidsvalidator/current/.env` on the box and make the GitHub Secrets match it** (then add the LLM key).

2. **Python version hardcode.** `fabrictasks.py` line ~34 hardcodes the migrations path as `.../lib/python3.8/site-packages/migrations`. If the production venv is **not** Python 3.8, change `python3.8` in that line to the venv's actual version, or the `flask db upgrade` step fails. Check with `/opt/afidsvalidator/venv-afidsvalidator/bin/python --version`.

3. **RAG ingestion is NOT required.** Do **not** run `flask ingest-knowledge` against the Groq key — Groq serves chat models only, no embeddings. The tutor degrades gracefully to built-in landmark reference material without an embeddings store, so it works fine with no ingestion.

4. **The `Dockerfile` bit-rot is irrelevant to this deploy.** Production builds a wheel, not a Docker image, so the (currently broken) Dockerfile does not block deployment. It only affects local `docker compose`.

---

## 7. One-line summary

Point `PRODUCTION_URL` + `PRIVATE_KEY` at the current server, make the 2023 DB/secret values match what's actually on the box, confirm the venv's Python version for the migrations path, then run the **AFIDs Validator Deploy** workflow against `enh/ai-tutor-learning-mode`. The Groq key is already configured; the tutor goes live automatically once the branch is deployed.
