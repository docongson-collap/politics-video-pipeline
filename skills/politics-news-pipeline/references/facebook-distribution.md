# Facebook distribution (ShardBrowser profile "Facebook")

## Hard boundary
- Politics manages ONLY the ShardBrowser profile named exactly "Facebook". Never start, stop, or read any other profile
  (they belong to other projects: Flight Anatomy, Broken Price Tag, Life Across the Map...). Listing /profiles only to find
  this one by name is fine; nothing else. tools/shard_fb.py hard-codes NAME = "Facebook" — keep it that way.
- Do not open new accounts/profiles. New Pages (if needed) are created inside this one account, only after owner approves and the
  channel name exists (docs/CHANNEL.md). Never post politics to the account's existing Vietnamese parenting Pages.

## How the profile is driven (pattern copied from Aviation tools/shard_*.py)
1. Import the local ShardBrowser API helper from /Volumes/WORK/Application/shard_migrate.py via importlib with
   sys.argv temporarily set to ["x","__none__"] (otherwise it runs a migration). Auth = JWT from launcher settings; never print it.
2. GET /profiles -> pick name == "Facebook". If `running` is true, someone is using it: abort, do not stop it.
3. POST /profiles/{id}/start {"headless": true} -> cdp.port; sleep ~5 s.
4. PUT http://127.0.0.1:{port}/json/new?about:blank -> websocket; drive with CDP (Page.navigate, Runtime.evaluate,
   Input.insertText, DOM.setFileInputFiles for uploads).
5. Always POST /profiles/{id}/stop in a finally block.
- Traffic goes through the profile's own proxy (verify via ipinfo.io inside the profile), never the Mac IP.
- Run with ~/.hermes/hermes-agent/venv/bin/python (has websockets).
- `python tools/shard_fb.py check control/facebook/check_<ts>.json` = read-only health: proxy IP, logged_in, /me URL, Pages list.

## Facebook post packaging (differs from YouTube)
- Title: sentence case, no ALL-CAPS words (reads as clickbait on FB); lead with the on-tape quote or the contradiction.
- Post text: open with the exact on-tape quote, 4-6 short paragraphs of the story with exact quoted filing lines, verdict
  marked "In our view", the denial/attribution line for any allegation, 3-5 hashtags. No chapters.
- Source links go in the FIRST COMMENT, not the post body (external links cut reach).
- Save as cases/<slug>/delivery/facebook.md (title + 2 alts, post text, first comment).
