"""blanche-huang-confession graphics plan (WO graphics 2026-11-25).

CAPS: capture key -> url + options. A mark string "ctx||target" = find ctx verbatim on the page, mark only target inside it.
      Suffix "##N" = use the N-th visible occurrence of ctx (1-based; e.g. skip a breadcrumb copy of a title).
ROWS: one entry per graphic row of edit/shotmap_v1.tsv (WEBHEAD / POST / SPLIT / NUM / DOC = 62), marks as
      (mark string, a, b): a = marker start (the first voiced word start, words.json), b = marker end (last voiced word end).
      Default marks = the shot-map's evidence phrase verbatim with the shot-map's times; MARKS overrides rows whose shot-map
      phrase is elided ("...") or not verbatim on the page.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shotrows import rows as _rows  # noqa

U = "https://"
CAPS = {
 "CNBCT":    {"url": U + "www.cnbc.com/2026/11/23/cnbc-transcript-president-donald-trump-speaks-with-cnbcs-eamon-javers-and-squawk-on-the-street-today.html"},
 "CNBCT_S":  {"url": U + "www.cnbc.com/2026/11/23/cnbc-transcript-president-donald-trump-speaks-with-cnbcs-eamon-javers-and-squawk-on-the-street-today.html",
              "vw": 480, "origin": "CNBCT", "via": "same CNBC transcript page at a 480 px viewport (SPLIT pane: narrow column so the quote reads at half-frame width)"},
 "CNBC1124": {"url": U + "www.cnbc.com/2026/11/24/nvidia-jensen-huang-fbi-doj-patel-blanche.html"},
 "FOXA":     {"url": U + "www.foxnews.com/politics/doj-recovers-8b-charges-more-than-800-suspects-largest-anti-scam-surge-history"},
 "NBC":      {"url": U + "www.nbcnews.com/politics/trump-administration/todd-blanche-nvidia-investigation-ceo-jensen-huang-trump-rcna611132"},
 "AJZ":      {"url": U + "www.aljazeera.com/news/2026/11/24/todd-blanche-declines-to-confirm-if-nvidias-jensen-huang-was-investigated", "hide_media": True},
 "NYPP":     {"url": U + "nypost.com/2026/11/24/us-news/trump-leaves-door-open-to-jensen-huang-pardon-and-urges-him-not-to-plead-5th-to-congress-next-week/", "hide_media": True},
 "JSPR":     {"url": U + "www.justice.gov/opa/pr/joint-statement-department-commerce-and-department-justice-megaspeed-investigation"},
 "CNNT":     {"url": U + "transcripts.cnn.com/show/sotu/date/2026-11-22/segment/01", "vw": 760},   # full-width transcript lines -> narrow viewport so lines wrap to a phone-readable measure
 "DOJSDNY":  {"url": U + "www.justice.gov/opa/pr/three-charged-conspiring-unlawfully-divert-cutting-edge-us-artificial-intelligence"},
 "DOJSDNY_WB": {"url": "https://web.archive.org/web/20261117203153/https://www.justice.gov/opa/pr/three-charged-conspiring-unlawfully-divert-cutting-edge-us-artificial-intelligence",
              "origin": "DOJSDNY", "via": "live capture matched only the breadcrumb copy of the title and justice.gov timed out (curl + browser) on re-capture -> Wayback 20261117203153 copy of the same release"},
 "PBSA":     {"url": U + "www.pbs.org/newshour/politics/what-trump-told-pbs-news-about-jensen-huang-before-nvidia-reinstatement", "vw": 760, "hide_media": True},
 "CNBC1123": {"url": U + "www.cnbc.com/2026/11/23/anthropic-nvidia-shares.html"},
 "CNBC1116": {"url": U + "www.cnbc.com/2026/11/16/trump-nvidia-stock-trades-jensen-huang.html"},
 "CNBC1116_N": {"url": U + "www.cnbc.com/2026/11/16/trump-nvidia-stock-trades-jensen-huang.html", "vw": 640, "dpr": 3, "origin": "CNBC1116",
              "via": "same CNBC Nov 16 page at a 640 px viewport, DPR 3 (NUM: the real figure lines are lifted large, so they need more source pixels)"},
 "ABCWH":    {"url": U + "abcnews.com/US/trump-owned-12-million-nvidia-stock-end-year/story?id=138393684"},
 "CNBC1109": {"url": U + "www.cnbc.com/2026/11/09/nvidia-jensen-huang-china-spy-trump-lobbying.html", "hide_media": True},
 "CNBC1015": {"url": U + "www.cnbc.com/2026/10/15/trump-ballroom-nvidia-cisco-donations.html"},
 "MEDIAITE": {"url": "https://web.archive.org/web/20261111142921/https://www.mediaite.com/media/news/todd-blanche-wildly-claims-doj-independence-is-a-misperception-i-work-for-president-trump/",
              "via": "mediaite.com shows a Cloudflare 'Just a moment...' wall -> Wayback 20261111142921 copy of the same article"},
 "TNR":      {"url": U + "newrepublic.com/post/216921/todd-blanche-department-justice-supposed-run-president-whims"},
 "OAG":      {"url": U + "oag.ca.gov/news/press-releases/attorney-general-bonta-serves-investigative-subpoena-nvidia"},
 "CNNRK":    {"url": U + "www.cnn.com/2026/11/24/politics/video/jamie-raskin-todd-blanche-donald-trump-jensen-huang-nvidia-department-of-justice-attorney-general-pardon-congress", "raw": True,
              "via": "live; viewport capture without clean-up JS (CNN's video page drops its visible headline when the viewport is resized)"},
 "NYPR":     {"url": U + "nypost.com/2026/11/24/us-news/rubio-jensen-huangs-nvidia-as-malign-influence-before-ouster", "hide_media": True},
 "FORT":     {"url": U + "fortune.com/2026/11/17/jensen-huang-nvidia-house-committee-return-ceo-testimony/"},
 "JEFF":     {"url": U + "jeffries.house.gov/2026/11/23/speaker-designate-jeffries-statement-on-the-reinstatement-of-jensen-huang-as-ceo-of-nvidia"},
 "BLAW":     {"url": U + "news.bloomberglaw.com/artificial-intelligence/blanche-says-doj-probe-into-huang-hasnt-been-discussed-publicly"},
 "BLAW_S":   {"url": U + "news.bloomberglaw.com/artificial-intelligence/blanche-says-doj-probe-into-huang-hasnt-been-discussed-publicly", "vw": 480, "origin": "BLAW",
              "via": "same Bloomberg Law page at a 480 px viewport (SPLIT pane)"},
 "XSCH":     {"url": U + "platform.twitter.com/embed/Tweet.html?id=2125288276034543676&theme=light&dnt=true", "vw": 560, "dpr": 3, "raw": True,
              "origin": "XSCH (https://x.com/SenSchumer/status/2125288276034543676)",
              "via": "x.com returns HTTP 403 logged out and Wayback has no snapshot -> X's own embed renderer (platform.twitter.com) of the same post ID"},
}
PDFS = {   # key -> (pdf file in work/pdf, page, url, via)
 "FEDREG_p2": ("FR.pdf", 2, "https://public-inspection.federalregister.gov/2026-23999.pdf", "live PDF (curl)"),
 "FEDREG_p8": ("FR.pdf", 8, "https://public-inspection.federalregister.gov/2026-23999.pdf", "live PDF (curl)"),
 "JSPDF_p1":  ("JS.pdf", 1, "https://www.justice.gov/opa/media/1472536/dl?inline=", "live PDF (curl)"),
}

JS_TITLE = "Joint Statement from Department of Commerce and Department of Justice on Megaspeed Investigation"
# (seg, t0) -> (capture key, [(mark, a, b)])
MARKS = {
 ("B5", 0.00): ("AJZ", [("Even the reporting from the various leaks or sources", 0.47, 1.01),
                        ("didn't suggest that Huang himself was under some sort of investigation", 1.01, 3.73)]),
 ("B6", 15.27): ("FEDREG_p2", [("Additions to the Entity List", 15.52, 16.08), ("PT Megaspeed International", 16.08, 16.38),
                               ("Megaspeed (Thailand) Co., Ltd.", 16.30, 16.52)]),
 ("B6", 16.60): ("FEDREG_p8", [("Filed: 11/23/2026", 16.76, 17.90)]),
 ("B6", 29.66): ("JSPR", [(JS_TITLE + "||Joint Statement##2", 29.91, 30.92), (JS_TITLE + "||on Megaspeed Investigation##2", 30.92, 31.64),
                          (JS_TITLE + "||Department of Justice##2", 32.24, 34.05)]),
 ("B9", 6.96): ("CNNT", [("BASH: And they were successful? China has these chips?||BASH", 7.44, 8.04),
                         ("BASH: And they were successful? China has these chips?||China has these chips?", 8.61, 10.08)]),
 ("B12", 6.72): ("CNBC1116_N", [("bought and sold Nvidia stock at least 103 times||103", 6.97, 7.96)]),
 ("B12", 17.51): ("CNBC1116_N", [("worth between $12.5 million and $58 million||$12.5 million and $58 million", 17.76, 21.22)]),
 ("B12", 21.18): ("CNBC1116_N", [("the filings give broad dollar ranges", 22.60, 24.96)]),
 ("B16", 6.57): ("CNNRK", [("Raskin: Blanche's answers on Nvidia were breathtaking \"gobbledygook\"||Blanche's answers on Nvidia##1", 6.82, 8.26)]),
 ("B17", 1.89): ("CNNRK", [("Raskin: Blanche's answers on Nvidia were breathtaking \"gobbledygook\"||breathtaking \"gobbledygook\"##1", 2.14, 3.44)]),
 ("B4", 1.72): ("AJZ", [("What does that mean, 'Had Huang been investigated'||Huang been investigated", 1.76, 3.30)]),   # voice: "Huang been investigated?"; NBC's line sits between two 'spy' lines -> AJZ (logged)
 ("B14", 5.33): ("TNR_TOP", [("The New Republic", 5.77, 6.51)]),
 ("B10", 8.65): ("DOJSDNY_WB", [("Three Charged with Conspiring to Unlawfully Divert Cutting Edge U.S. Artificial Intelligence Technology to China||Unlawfully Divert Cutting Edge U.S. Artificial Intelligence Technology to China##2", 8.90, 12.84)]),
 ("B10", 13.75): ("DOJSDNY", [("approximately $510 million", 14.00, 15.21), ("Between late April 2025 and mid-May 2025", 17.12, 18.76)]),   # 'Three Charged' (title, 2,460 px up) / 'are each charged' (1,850 px down) cannot share the frame -> not marked (logged)
 ("B14", 0.00): ("MEDIAITE", [("criticizing Biden-era Attorney General Merrick Garland", 0.74, 2.40),
                              ("Claims DOJ Independence is a 'Misperception'||DOJ Independence is a 'Misperception'", 4.90, 5.37)]),
 ("B6", 3.67): ("JSPDF_p1", [("November 16, 2026", 3.92, 4.40),
                             ("JOINT STATEMENT FROM DEPARTMENT OF COMMERCE AND DEPARTMENT OF JUSTICE ON MEGASPEED INVESTIGATION", 4.64, 6.00)]),
 ("B6", 6.34): ("JSPDF_p1", [("update on the investigation of the Singaporean company Megaspeed", 8.80, 11.20)]),
 ("B18", 20.36): ("FORT", [("Huang will appear Dec. 1", 20.40, 22.04)]),   # voice "Huang appears December 1st"; body line, same frame as B18 17.46 (orchestrator re-marked cap/FORT.json)
 ("B11", 19.21): ("BLAW_S", [("says on Fox News", 19.46, 20.40), ("when asked if an investigation into Jensen Huang is closed", 20.91, 22.95)]),
 ("B18", 20.36): ("FORT", [("Huang will appear Dec. 1", 20.40, 22.04)]),   # orchestrator 12:45: body line instead of photo caption
 ("B11", 23.26): ("BLAW_S", [("That assumes there is an investigation that's open", 24.26, 26.86), ("that's never been discussed publicly", 27.03, 29.20)]),   # voiced from "that's" 27.03
}

# extra phrases per capture (composites / framing), captured alongside the row marks
EXTRA = {
 "CNBCT_S": ["They did a pretty good investigation, and they felt that he himself was was exonerated."],
 "BLAW_S": ["That assumes there is an investigation that's open, and that's never been discussed publicly"],
 "CNBC1116_N": ["bought and sold Nvidia stock at least 103 times||at least 103 times",
                "But the filings give broad dollar ranges for holdings rather than the number of shares, leaving his current stake unclear."],
 "XSCH": ["Chuck Schumer", "@SenSchumer", "12:59 AM · Nov 25, 2026"],
}

ROWS = []
for r in _rows():
    k = (r["seg"], round(r["t0"], 2))
    if k in MARKS:
        key, mk = MARKS[k]
    else:
        key, mk = r["key"], [(e, a, b) for e, a, b in r["marks"]]
    if r["treat"] == "SPLIT":
        key = "CNBCT_S+BLAW_S"
    ROWS.append(dict(r, cap=key, mk=mk))

if __name__ == "__main__":
    for r in ROWS:
        print(r["line"], r["seg"], r["t0"], r["t1"], r["treat"], r["cap"], r["mk"])
    print(len(ROWS))

# per-row vertical limits for page frames (CSS px) when a page element must stay out of frame
YLIM = {"B10_33.56": (0, 2530)}   # AJZ: keep the empty "Advertisement" box (y 2540+) out of frame
# rows rendered as one real page block on the navy backing instead of a page window (reason in build_graphics.build_card)
CARD = {"B12_1.72": ("CNBC1116", None),          # CNBC Nov 16: KEY POINTS bullet 1 only ('spy' sits on the next bullet, y 867)
        "B14_5.33": ("TNR_TOP", [0, 0, 1440, 160]),  # TNR masthead strip: the wordmark is 956 px wide, a 16:9 page window cut it
        "B15_4.77": ("NYPP", [186, 2445, 940, 2598]),   # NY Post: empty ADVERTISEMENT slot right above the quote
        "B15_11.44": ("NYPP", [186, 1775, 940, 1900]),  # NY Post: empty EXPLORE MORE promo right below the quote
        "B15_25.78": ("OAG", [140, 405, 1300, 725]),    # CA AG: page ends at 1231 px, a 16:9 window half-cut the contact line
        "B15_29.09": ("OAG", [140, 793, 1300, 1022]),   # CA AG: 'spy' on the line right above (y 764-787) -> block starts below it
        "B16_6.57": ("CNNRK", [16, 588, 944, 880]),     # CNN video page: headline block only (player above is an unloaded black box)
        "B17_1.89": ("CNNRK", [16, 588, 944, 880]),
        "B14_0.00": ("MEDIAITE", [[100, 40, 940, 290], [119, 1005, 935, 1097]]),  # headline + 'criticizing ... Garland' paragraph are 800 px apart -> two stacked cards
        }
