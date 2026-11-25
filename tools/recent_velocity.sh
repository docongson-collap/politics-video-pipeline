#!/usr/bin/env bash
# Pull upload date + views for the latest N uploads of each competitor channel.
# Usage: tools/recent_velocity.sh [N]   -> docs/research/comp/<channel>_recent.tsv
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
N="${1:-15}"
OUT="$ROOT/docs/research/comp"; mkdir -p "$OUT"
FMT='%(id)s	%(upload_date)s	%(view_count)s	%(duration)s	%(channel_follower_count)s	%(title)s'
# Rival handles: docs/COMPETITORS.md
for c in briantylercohen MeidasTouch thehillnews; do
  yt-dlp --playlist-end "$N" --skip-download --sleep-requests 1 --print "$FMT" \
    "https://www.youtube.com/@$c/videos" > "$OUT/${c}_recent.tsv" 2> "$OUT/${c}.err"
  echo "$c rows=$(wc -l < "$OUT/${c}_recent.tsv") errors=$(grep -c ERROR "$OUT/${c}.err")"
done
