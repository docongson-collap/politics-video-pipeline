# Rival research recipe (Politics)

Outputs live in docs/research/competitors/ (discovery/ = raw). Summaries go to docs/COMPETITORS.md and stance_analysis.md.

## 1. Discover channels (yt-dlp, free)
- 20-30 story/lane queries of the week -> YouTube search filtered to this week:
  `https://www.youtube.com/results?search_query=<q>&sp=EgIIAw%253D%253D` with
  `yt-dlp --flat-playlist --playlist-items 1-40 --print "%(channel_id)s|%(channel)s|%(view_count)s|%(duration)s|%(id)s|%(title)s"`.
- Parse with an anchored regex on the UC id (channel names contain `|`/spaces; naive split breaks). Rank channels by summed views.

## 2. Profile each candidate
- `yt-dlp --flat-playlist -J --playlist-items 1-30 --extractor-args youtubetab:approximate_date <channel_url>/videos`
  -> subs (channel_follower_count), uploads/day, median views, median length, VPH of 1-14-day-old videos. Use /channel/<UCid>/ when
  the handle is unknown; resolve a name with `ytsearch1:<name>` and read channel_url.
- Contact sheet of 4 latest thumbs per channel (i.ytimg.com/vi/<id>/mqdefault.jpg, PIL) and LOOK: host face vs faceless vs AI/slop.
- Classify: same-stance host / same-stance faceless / slop (fabricated quotes, "Congress votes to REMOVE Trump") / neutral aggregator.

## 3. Stance corpus (how rivals express the view)
- Select ~15 latest long (>4 min) videos x ~10 same-stance channels (BTC from docs/research/btc_catalog.tsv).
- Captions: `yt-dlp --no-update --skip-download --write-auto-subs --sub-langs en-orig --sub-format vtt -o "%(id)s"`.
  Run serially with --sleep-subtitles 4 + sleep 3 between videos, in background with notify: parallel xargs -P4 hits HTTP 429
  after ~30 videos; paced serial runs clean. Re-run only the missing ids (grep -vxFf have.txt ids.txt).
- VTT -> text: discovery/stance_corpus/vtt2txt.py (dedupes rolling caption lines, prefers en-orig).
- Code every transcript with discovery/stance_corpus/CODEBOOK.md (story_type, antagonist, opener_type, labels, insult_level,
  evidence devices, prescription, verdict_quote, close_type, cta_identity, persona) via <=5 Claude subagents, one JSONL line/video;
  aggregate in Python per channel.
- Titles: ~200 latest per channel (`--flat-playlist --playlist-items 1-200 --print "%(view_count)s\t%(duration)s\t%(title)s"`);
  regex features (targets: Trump/GOP/Fox/DOJ; verbs: panic, caught, humiliate, loses, stunned, consequence, call out) -> share per
  channel and view lift = median(views / channel median) with vs without the feature.
- Auto-captions misspell names: verify any quote against the source audio before using it in a video.
