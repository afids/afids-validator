#!/usr/bin/env bash
# Capture the /learn interface screenshots used by Figure 0 (graphical abstract)
# and Figure 1 in make_figures.py.
#
# Requirements: a running instance and the `agent-browser` CLI
# (npm i -g agent-browser  ||  brew install agent-browser; agent-browser install).
#
# Usage:
#   DATABASE_URL="sqlite:///afids_dev.db" FLASK_APP=afidsvalidator \
#     flask run --port 5001 &        # start the app (Ollama or an LLM key running)
#   ./capture_screenshots.sh
#
# Writes paper_figures/ss_learn_hero.png (a placed-fiducial session state).
set -euo pipefail

URL="${LEARN_URL:-http://127.0.0.1:5001/learn}"
OUT="paper_figures"
S="afids"

agent-browser --session "$S" set viewport 1500 1180 2
agent-browser --session "$S" open "$URL"
agent-browser --session "$S" wait --load networkidle
agent-browser --session "$S" wait --text "Anterior Commissure"
sleep 4
# place a fiducial at the default crosshair to surface the rater-calibrated badge
PLACE=$(agent-browser --session "$S" snapshot -i | grep -i "Place Fiducial" | grep -oE "@e[0-9]+" | head -1)
agent-browser --session "$S" click "$PLACE"
agent-browser --session "$S" wait --text "trained raters"
sleep 9   # let the feedback finish streaming
agent-browser --session "$S" screenshot "$OUT/ss_learn_hero.png"
agent-browser --session "$S" close
echo "wrote $OUT/ss_learn_hero.png"
