#!/usr/bin/env bash
# Merge latest Comfy-Org/ComfyUI into this fork. Never pushes to upstream.
set -euo pipefail
cd "$(dirname "$0")"

git fetch upstream
git fetch origin

echo "Merging upstream/master into $(git branch --show-current)..."
git merge upstream/master --no-edit

echo "Pushing to origin (your fork) only..."
git push origin HEAD

echo "Done."
git rev-list --left-right --count upstream/master...HEAD | awk '{print "ahead of upstream by "$2" commit(s); upstream-only="$1}'
