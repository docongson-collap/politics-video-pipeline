#!/usr/bin/env bash
# Run one Politics-channel role on its assigned model.
# Usage: tools/role.sh <role> <work-order.md>
# Roles + models: docs/ROSTER.md (this file is the source of truth for the mapping).
#
# Mechanisms:
#  - model/provider/toolsets are fixed per role here; the WO cannot change them;
#  - the WO must declare "OUTPUT: <path>" lines; the run FAILS (exit 3) unless every
#    output exists and was written during this run;
#  - full transcript -> work-orders/logs/.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROLE="${1:-}"; WO="${2:-}"
[[ -z "$ROLE" || -z "$WO" ]] && { echo "usage: tools/role.sh <role> <work-order.md>"; exit 2; }
[[ -f "$WO" ]] || { echo "WO not found: $WO"; exit 2; }
[[ -n "${POL_ROLE_CHILD:-}" ]] && { echo "BLOCKED: role.sh called from inside a role run ($POL_ROLE_CHILD). Do the work yourself; never re-dispatch."; exit 2; }
WO="$(cd "$(dirname "$WO")" && pwd)/$(basename "$WO")"

case "$ROLE" in
  scout)      PROV=anthropic; MODEL=claude-haiku-4-5; TOOLS=browser,web,file,terminal,vision ;;
  researcher) PROV=anthropic; MODEL=claude-sonnet-4-6; TOOLS=web,file,terminal ;;
  writer)     PROV=anthropic; MODEL=claude-sonnet-5-5; TOOLS=file ;;
  factcheck)  PROV=anthropic; MODEL=claude-sonnet-5-5; TOOLS=web,file ;;
  visual)     PROV=anthropic; MODEL=claude-opus-5-5; TOOLS=browser,web,file,terminal,vision ;;
  builder)    PROV=anthropic; MODEL=claude-sonnet-5; TOOLS=file,terminal,vision,code_execution ;;
  qc)         PROV=anthropic; MODEL=claude-sonnet-5; TOOLS=file,terminal,vision ;;
  packaging)  PROV=anthropic; MODEL=claude-haiku-4-5; TOOLS=browser,web,file,terminal,vision ;;
  *) echo "unknown role: $ROLE (scout researcher writer factcheck visual builder qc packaging)"; exit 2 ;;
esac
# 2026-11-06: all roles on Claude via the Hermes Anthropic credential (copy Aviation). No OmniRoute, no 9router.
# Override the Claude model for one run: ROLE_MODEL=claude-sonnet-5 tools/role.sh ...
[[ -n "${ROLE_MODEL:-}" ]] && { PROV="${ROLE_PROV:-$PROV}"; MODEL="$ROLE_MODEL"; }

LOGDIR="$ROOT/work-orders/logs"; mkdir -p "$LOGDIR"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="$LOGDIR/$STAMP-$ROLE-$(basename "$WO" .md).log"


OUTPUTS=$(grep -E '^OUTPUT:' "$WO" | sed -E 's/^OUTPUT:[[:space:]]*//')
[[ -z "$OUTPUTS" ]] && { echo "WO has no 'OUTPUT: <path>' line — refusing (DONE-WHEN must be checkable)"; exit 2; }
if [[ "$ROLE" == writer ]] && ! grep -qE '^PARITY:' "$WO"; then
  echo "writer WO has no 'PARITY: <script> <rival transcript>' line — refusing (LESSONS 2026-10-16)"; exit 2
fi
MARK="$(mktemp "$LOGDIR/.mark.XXXX")"

CARD=$(awk -v r="## role: $ROLE" '$0==r{f=1;next} /^## role: /{f=0} f' "$ROOT/docs/ROSTER.md")
PROMPT="You are the Politics (faceless US political news YouTube channel, rival @briantylercohen) role '$ROLE'. Project root: $ROOT
Work only inside the project root. Answer in English. Do not commit to git. Never print secrets.

ROLE CARD (from docs/ROSTER.md):
$CARD

HARD RULES (from CLAUDE.md, abridged):
- No invented numbers, causes, quotes or engineering claims; every important fact carries a source URL.
- Lifetime-average VPH never passes the demand gate; only a live vidIQ badge does.
- New output version = new file; never overwrite older versions.
- No paid TTS, no rendering of a full video unless the WO says so.

WORK ORDER ($WO):
YOU are the $ROLE doing this WO now. Never run tools/role.sh or any runner; do the work directly with your tools.
$(grep -v '^Run: tools/role.sh' "$WO")

When finished, reply with: DONE or BLOCKED, then one line per OUTPUT path with what it contains."

echo "[$STAMP] role=$ROLE provider=$PROV model=$MODEL tools=$TOOLS wo=$WO" | tee "$LOG"
cd "$ROOT"
POL_ROLE_CHILD="$ROLE" env -u HERMES_SESSION_ID -u HERMES_SESSION_KEY -u HERMES_PARENT_SESSION_ID -u TERMINAL_CWD \
  hermes -z "$PROMPT" --provider "$PROV" -m "$MODEL" -t "$TOOLS" --ignore-rules --yolo >>"$LOG" 2>&1
RC=$?
echo "[exit $RC]" >>"$LOG"

FAIL=0
while IFS= read -r o; do
  [[ -z "$o" ]] && continue
  p="$o"; [[ "$p" != /* ]] && p="$ROOT/$p"
  if [[ -f "$p" && "$p" -nt "$MARK" ]]; then echo "OUTPUT OK   $o" | tee -a "$LOG"
  else echo "OUTPUT MISSING/STALE  $o" | tee -a "$LOG"; FAIL=1; fi
done <<< "$OUTPUTS"
rm -f "$MARK"
# Word gate: WO line "MINWORDS: <file> <n> [min_avg_words_per_sentence]" — counts words between "## SCRIPT" and the next "## ".
# Lesson 2026-11-06 (prf script-v1: 2,184 words, 6.5 w/s, while its own STATS claimed 3,610).
MW=$(grep -E '^MINWORDS:' "$WO" | head -1 | sed -E 's/^MINWORDS:[[:space:]]*//')
if [[ -n "$MW" && $FAIL -eq 0 ]]; then
  set -- $MW
  python3 - "$ROOT/$1" "$2" "${3:-0}" <<'PY' 2>&1 | tee -a "$LOG"
import re,sys
t=open(sys.argv[1],encoding='utf-8').read()
m=re.search(r'^## SCRIPT\n(.*?)(?=^## )',t,re.S|re.M); body=m.group(1) if m else t
body=re.sub(r'\{C\d+\}|^\[B\d+\]\s*CHAPTER.*$','',body,flags=re.M)
body=re.sub(r'^\[B\d+\]','',body,flags=re.M)  # beat text may sit on the tag line (nz-exodus v1: counted 486 of 3,4xx)
w=len(body.split()); s=[x for x in re.split(r'[.!?]+\s',body) if x.strip()]
avg=w/max(1,len(s)); ok=w>=int(sys.argv[2]) and avg>=float(sys.argv[3])
print(f"MINWORDS: {w} words (min {sys.argv[2]}), avg {avg:.1f} w/s (min {sys.argv[3]}) -> {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
PY
  [[ ${PIPESTATUS[0]} -ne 0 ]] && FAIL=6
fi
# Rival parity gate: WO line "PARITY: <our script> <rival transcript> [--ignore Sponsor]".
# Writer output fails (exit 4) unless tools/rival_parity.py passes. Lesson 2026-10-16.
PARITY=$(grep -E '^PARITY:' "$WO" | head -1 | sed -E 's/^PARITY:[[:space:]]*//')
if [[ -n "$PARITY" && $FAIL -eq 0 ]]; then
  # shellcheck disable=SC2086
  set -- $PARITY
  OURS="$1"; RIV="$2"; shift 2
  python3 "$ROOT/tools/rival_parity.py" --ours "$ROOT/$OURS" --rival "$ROOT/$RIV" "$@" 2>&1 | tee -a "$LOG"
  [[ ${PIPESTATUS[0]} -ne 0 ]] && { echo "PARITY FAIL — rewrite closer to the rival" | tee -a "$LOG"; FAIL=4; }
fi
# Ledger gate: researcher outputs named *ledger*.md must have every quote on its source page.
# Lesson 2026-10-17 (dominos v1: 18/50 rows had dead URLs or quotes not on the page).
if [[ "$ROLE" == researcher && $FAIL -eq 0 ]]; then
  while IFS= read -r o; do
    [[ "$o" == *ledger*.md ]] || continue
    python3 "$ROOT/tools/ledger_verify.py" "$ROOT/$o" --out "$ROOT/${o%.md}_verify.md" 2>&1 | tail -1 | tee -a "$LOG"
    [[ ${PIPESTATUS[0]} -ne 0 ]] && { echo "LEDGER FAIL — see ${o%.md}_verify.md" | tee -a "$LOG"; FAIL=5; }
  done <<< "$OUTPUTS"
fi
tail -5 "$LOG" | sed 's/^/  /'
echo "log: $LOG"
[[ $RC -ne 0 ]] && exit 1
[[ $FAIL -eq 4 ]] && exit 4
[[ $FAIL -eq 5 ]] && exit 5
[[ $FAIL -eq 6 ]] && exit 6
[[ $FAIL -ne 0 ]] && exit 3
exit 0
