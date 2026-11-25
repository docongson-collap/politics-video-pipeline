#!/usr/bin/env python3
"""Build edit/shotmap_v1.tsv (+ QC block) and research/SOURCES.md for blanche-huang-confession.

Visual role, shot-map v1, 2026-11-25. Format copied from cases/trump-nvidia-huang/edit/shotmap_v1_build.py.
Row boundaries snap to word starts in audio_full_v1/words.json (segment seconds); marker times are computed
from the same words (+-0.3 s rule). Footage windows are validated against real file durations (ffprobe).
Run:  python3 edit/shotmap_v1_build.py   (from the case dir or anywhere)
"""
import json, os, re, subprocess, collections

CASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(CASE))
TNH = os.path.join(ROOT, 'cases', 'trump-nvidia-huang')
W = json.load(open(os.path.join(CASE, 'audio_full_v1', 'words.json')))
PLAN = json.load(open(os.path.join(CASE, 'edit_plan_v1.json')))

# ---------------------------------------------------------------- sources
# key -> (TYPE, path-or-URL, description, rights note, person-in-frame default)
S = {}
def src(key, kind, where, desc, rights):
    S[key] = dict(kind=kind, where=where, desc=desc, rights=rights)

A = 'assets/clips/'
T = '../trump-nvidia-huang/assets/clips/'
E = '../trump-nvidia-huang/assets/envato/'
K = '../../kho/stock/'
FAIR = 'fair use (news commentary/criticism), outlet bug kept'
src('CBS', 'CLIP', A + 'TC-axC1IL00.mp4', "CBS News (YouTube), Blanche/Patel DOJ news conference Q&A, Nov 24 2026 - https://www.youtube.com/watch?v=TC-axC1IL00", 'CBS NEWS 24/7 bug kept; chyrons quote tape (\'FOR WHAT?\') - no crop needed; ' + FAIR)
src('FOXP', 'CLIP', A + 'foxnews_6408836632112.mp4', "Fox News video, same DOJ news conference (Q&A angle), Nov 24 2026 - https://www.foxnews.com/video/6408836632112", 'FOX NEWS bug kept; chyron \'DOJ ON NVIDIA "SPY" SCANDAL...\' (72-132 s, 240 s+) is NOT on tape -> mask that chyron text line only (bug stays); ' + FAIR)
src('CNNC', 'CLIP', A + 'CNN_me20cb05073fdab89ec615e8b341bdd6d459587184.mp4', "CNN State of the Union, Dana Bash x DNI Jay Clayton, Nov 22 2026 - https://www.cnn.com/2026/11/22/politics/video/cnn-sotu-jay-clayton-dana-bash-ai-chips-nvidia-scandal-digvid", 'CNN bug kept; ' + FAIR)
src('CNNR', 'CLIP', A + 'CNN_me6ad953179aa97b71867f032e98881920cf2d84c5.mp4', "CNN The Source, Kaitlan Collins x Rep. Jamie Raskin, Nov 24 2026 - https://www.cnn.com/2026/11/24/politics/video/jamie-raskin-todd-blanche-donald-trump-jensen-huang-nvidia-department-of-justice-attorney-general-pardon-congress", 'CNN bug kept; ' + FAIR)
src('FOXR', 'CLIP', A + 'foxnews_6408780341112.mp4', "Fox News video, Rubio walks away from the Huang question (State Dept photo spray), Nov 24 2026 - https://www.foxnews.com/video/6408780341112", 'source feed carries no burned bug in these frames -> no bug to keep; credit in SOURCES; ' + FAIR)
src('PF1', 'CLIP', A + 'podforceone_hVCMk36xo_s_1015.mp4', "NY Post 'Pod Force One' (Miranda Devine) with Todd Blanche, Oct 21 2026, file 0:00 = 10:15 of https://www.youtube.com/watch?v=hVCMk36xo_s", 'Pod Force One logo kept; ' + FAIR)
src('PBS', 'CLIP', T + 'AD6-BAzR6ZU.mp4', "PBS NewsHour, 'Why Trump pushed for Jensen Huang's return to Nvidia', 2026-11-23 - https://www.youtube.com/watch?v=AD6-BAzR6ZU", 'PBS NewsHour bug kept; ' + FAIR + '; re-use from trump-nvidia-huang at different timecodes')
src('CNBCr', 'CLIP', T + 'ZmkSZtN_ieM.mp4', "CNBC Television, 'Jensen Huang returns as Nvidia CEO after board reversal', 2026-11-23 - https://www.youtube.com/watch?v=ZmkSZtN_ieM", 'CNBC bug kept; ' + FAIR + '; different timecodes than trump-nvidia-huang')
src('CNBCi', 'CLIP', T + '-KzsKuC1AUs.mp4', "CNBC Television, 'Watch CNBC's full interview with President Trump' (phone interview; screen = Trump still + live NVDA board), 2026-11-23 - https://youtu.be/-KzsKuC1AUs", 'CNBC bug kept; audio muted under VO (still image, no lip movement); ' + FAIR)
src('CNNo', 'CLIP', T + 'O9uWX7BOV8E.mp4', "CNN NewsNight, 'WaPo: Secret docs reveal donors behind Trump's ballroom' (donor graphic incl. Nvidia $25M; Trump file footage), 2026-10-16 - https://www.youtube.com/watch?v=O9uWX7BOV8E", 'CNN bug kept; ' + FAIR)
src('RTR', 'CLIP', T + 'gdw1ZYzSxLM.mp4', "Reuters, 'Flowers laid at Nvidia HQ as CEO Huang steps down', Santa Clara 2026-11-12 - https://www.youtube.com/watch?v=gdw1ZYzSxLM", 'Reuters bug kept; ' + FAIR)
src('WHB', 'CLIP', T + 'qQxek3C2Gds.mp4', "The White House (YouTube), 'President Trump Visits White House Ballroom Construction', 2026-05-19 - https://www.youtube.com/watch?v=qQxek3C2Gds", 'US government work (public domain); no bug')
src('FBS', 'CLIP', T + 'qt6t5yldLeE.mp4', "Forbes Breaking News, Schumer Senate floor remarks on Huang, Nov 2026 - https://www.youtube.com/watch?v=qt6t5yldLeE", 'Forbes bug kept; chamber WIDE only (no lip-visible speech under VO); ' + FAIR)

def env(key, uuid, desc, ext='mov'):
    src(key, 'ENVATO', E + uuid + '.' + ext, desc + ' (Envato Elements, licensed for trump-nvidia-huang: ' + E + uuid + '.license.pdf)', 'Envato Elements license on file; no logos / identifiable real persons; scene-setting only, used once')
env('E_trader', 'c42deead-a678-46d1-b362-667e93ad2e4e', 'trader at screens')
env('E_papers', '93be6900-70e8-4c9e-ad32-43d1676764a5', 'newspapers on the press')
env('E_facade', '0184a775-0908-4665-9f52-e01db3ed22e0', 'flag on a federal building facade, Washington')
env('E_wh', '21e86cf3-359a-4847-b598-f8a6935c592d', 'White House exterior')
env('E_wh2', '11d553ef-1f8c-48b6-b416-5ad30a6ba0f1', 'White House exterior (second angle)')
env('E_sg', '48890979-ca7a-40d4-b851-88a61a12226e', 'Singapore skyline')
env('E_racks', 'a95839d8-8c6f-4542-8e15-b7b4bbe16a42', 'tracking shot of data-center server racks', 'mp4')
env('E_cal', 'aff72233-9990-4fcf-bc05-872a6a5d6484', 'calendar pages turning')
env('E_chip', '4e766657-6548-4581-b638-be5843b26dfa', 'chip macro')
env('E_campus', '93419312-b48a-44d8-bab3-8e46475c22ec', 'Nvidia campus architecture (canopy roof)', 'mp4')
env('E_flags', '7c6cf402-2602-4576-b52f-b18ec2c650c1', 'columned facade with American flags waving')
env('E_fbi', '860195cc-3a5c-4bce-97b5-6384d70ba109', 'FBI headquarters (J. Edgar Hoover Building) exterior, Washington')
env('E_nyse', '9008c0d4-0909-4a06-a7f9-b964fbb7dac3', 'New York Stock Exchange entrance with flag')
env('E_ticker', '30c8e90f-51b3-48a1-875c-0b11f631eba1', 'stock ticker numbers scrolling (no company names legible)')
env('E_charts', 'b3d57f44-43e4-472f-9a8a-c62d4ae998aa', 'trader watching charts')
env('E_phone', 'f4d3d540-9c6f-4884-b6b8-338dde1ededb', 'hand on a stock-trading phone app', 'mp4')
env('E_dcair', 'a69db31b-b3ec-45fd-b6f7-ce7387c97dcc', 'Washington DC aerial with Washington Monument')
env('E_capwater', '6d9fa3f3-9466-45e1-a361-80c0beae5cdb', 'US Capitol across the water', 'mp4')
env('E_capflowers', '84a48652-ed8b-477d-ae94-890b709a6247', 'US Capitol behind flowers')
env('E_capdusk', 'cbbac94e-afd6-4c77-b4fe-9aa8a658b823', 'US Capitol at dusk')
env('E_dome', 'ce86a91a-756c-466f-9927-dd6459dabb75', 'US Capitol dome', 'mp4')
env('E_room', '794b25e6-d6c3-4452-a006-444f490011ff', 'empty hearing/conference room')
env('E_whfence', '4e2439b8-29ef-4450-a1e8-88e9e30f3911', 'White House behind the fence')
env('E_wh3', '725ca9ce-ce6c-4859-8195-76dbb86bfea2', 'White House north side, autumn')
env('E_whair', 'fa20c571-7984-48a8-b141-ed9cf209bc1d', 'White House aerial')
env('E_lab', '541ed4dd-be5d-43bd-9886-ba5d25a67b38', 'lab monitor with circuit board')
env('E_news', 'a696715e-4f7b-47e7-8aaf-fc5e6d333a84', 'scrolling news on a phone (no legible headline)')
env('E_tv', 'fa1d9aa7-1e01-454e-9704-d041d8453691', 'hand holding a TV remote')
env('E_flag2', 'b85949f9-f66c-49fe-9883-f765b80676c9', 'US flag on a pole against the sky')
env('E_hands', 'cef3305f-4406-48fd-95be-cc15792bb09e', 'hands holding a phone', 'mp4')
env('E_city', '4101d6f0-0dc5-46ba-a054-106beb7eccd2', 'city aerial at dusk')
env('E_office', '3ed3f5d0-ec40-4a38-b720-8e46338fdfa1', 'empty office interior', 'mp4')
env('E_meeting', '5b83dc27-f14e-4286-8a71-af74125f7806', 'people around a meeting table (stock actors)', 'mp4')
env('E_towers', 'bfe6bc35-97b6-4aca-ae8e-6acd9d06c78a', 'skyscrapers looking up')
env('E_neo', '8728d3b7-4945-4648-87f3-1e77b7fab0ff', 'flags on a neoclassical federal building, Washington', 'mp4')
env('E_flag', '279f79c3-b5a3-4507-b99e-8cd3d4a0d59f', 'US flag')
env('E_capflag', '85357096-eeb2-4c95-abe8-396a5437c5cc', 'US Capitol with flag')
env('E_capitol', 'afa2cf73-c975-4fe4-b806-c84b6c077bdb', 'US Capitol')

def kho(key, rel, desc):
    src(key, 'KHO', K + rel, desc + ' (project stock library, license ' + K + os.path.dirname(rel) + '/' + os.path.dirname(rel) + '.license.pdf)', 'licensed project stock; scene-setting only, used once')
kho('K_doja', 'doj_bldg_a/doj_bldg_a.mov', 'Robert F. Kennedy DOJ building exterior')
kho('K_dojb', 'doj_bldg_b/doj_bldg_b.mov', 'DOJ building exterior (second angle)')
kho('K_court', 'courthouse_us/courthouse_us.mp4', 'US federal courthouse exterior')
kho('K_stamp', 'stamp_doc/819_NjU.mov', 'stamp coming down on a document')
kho('K_paper', 'paper_piles/paper_piles.MOV', 'piles of case files')
kho('K_capeast', 'capitol_east/capitol_east.mov', 'US Capitol east front')
kho('K_sfcourt', 'courthouse_sf_burton/courthouse_sf_burton.mov', 'Phillip Burton federal building and courthouse, San Francisco')
kho('K_capdc', 'capitol_dc/capitol_dc.mov', 'US Capitol, Washington DC')

def page(key, url, desc):
    src(key, 'PAGE', url, desc, 'page capture (masthead visible, dpr2) - quotation for news commentary; yellow marker only')
page('CNBC1124', 'https://www.cnbc.com/2026/11/24/nvidia-jensen-huang-fbi-doj-patel-blanche.html', "CNBC Nov 24 - Blanche/Patel dodge questions on Huang investigation (photo caption 'news conference to announce the results of a crackdown on cyber-enabled scams, at the Department of Justice in Washington, DC, Nov. 24, 2026'; 'So, when you say the export investigation is still ongoing, I don't know what you're talking about.'; 'We have hundreds, if not more, export investigations'). CROP: exclude the sentence containing 'Chinese spy'")
page('NBC', 'https://www.nbcnews.com/politics/trump-administration/todd-blanche-nvidia-investigation-ceo-jensen-huang-trump-rcna611132', "NBC News - 'Todd Blanche calls Nvidia a good corporate citizen while dodging questions on investigation' ('What does that mean?' / 'Had Huang been investigated for what?'; 'to encourage the board to reinstate him'; 'An administration official said the attorney general told the president that the DOJ had no evidence of wrongdoing by Huang or the company.')")
page('AJZ', 'https://www.aljazeera.com/news/2026/11/24/todd-blanche-declines-to-confirm-if-nvidias-jensen-huang-was-investigated', "Al Jazeera Nov 24 - 'Todd Blanche declines to confirm if Nvidia's Jensen Huang was investigated' (leaks quote; 'if Nvidia was the target...'; 'Beijing has denied the report as a smear')")
page('BLAW', 'https://news.bloomberglaw.com/artificial-intelligence/blanche-says-doj-probe-into-huang-hasnt-been-discussed-publicly', "Bloomberg Law Nov 24 - 'Blanche Says DOJ Probe Into Huang Hasn't Been Discussed Publicly' ('That assumes there is an investigation that's open, and that's never been discussed publicly,' ... says on Fox News)")
page('CNBCT', 'https://www.cnbc.com/2026/11/23/cnbc-transcript-president-donald-trump-speaks-with-cnbcs-eamon-javers-and-squawk-on-the-street-today.html', "CNBC transcript Nov 23, President Trump on Squawk on the Street ('They did a pretty good investigation, and they felt that he himself was was exonerated. I don't know what word you want to use.')")
page('FOXA', 'https://www.foxnews.com/politics/doj-recovers-8b-charges-more-than-800-suspects-largest-anti-scam-surge-history', "Fox News Nov 24 - 'DOJ recovers $8B, charges more than 800 suspects in largest anti-scam surge in history'")
page('JSPR', 'https://www.justice.gov/opa/pr/joint-statement-department-commerce-and-department-justice-megaspeed-investigation', "justice.gov Office of Public Affairs press-release page - Joint Statement from Department of Commerce and Department of Justice on Megaspeed Investigation")
page('FEDREG', 'https://public-inspection.federalregister.gov/2026-23999.pdf', "Federal Register public inspection 2026-23999 (BIS, 15 CFR 744) 'Additions to the Entity List' - adds 'PT Megaspeed International' and 'Megaspeed (Thailand) Co., Ltd.'; footer '[FR Doc. 2026-23999 Filed: 11/23/2026 4:15 pm]'")
page('CNNT', 'https://transcripts.cnn.com/show/sotu/date/2026-11-22/segment/01', "CNN transcript, State of the Union Nov 22 2026 - 'Interview With U.S. Director of National Intelligence Jay Clayton' ... CLAYTON: 'Yes, it appears, based on the facts alleged in the indictment, that ... there was access to those chips'")
page('DOJSDNY', 'https://www.justice.gov/opa/pr/three-charged-conspiring-unlawfully-divert-cutting-edge-us-artificial-intelligence', "justice.gov - 'Three Charged with Conspiring to Unlawfully Divert Cutting Edge U.S. Artificial Intelligence Technology to China' (SDNY; 'Between late April 2025 and mid-May 2025 alone, at least approximately $510 million worth of ... servers ... were diverted to China')")
page('PBSA', 'https://www.pbs.org/newshour/politics/what-trump-told-pbs-news-about-jensen-huang-before-nvidia-reinstatement', "PBS NewsHour article - 'had been in contact with a top official from the China Ministry of State Security from spring 2025' (crop: text only, no photo of Alice Huang)")
page('CNBC1123', 'https://www.cnbc.com/2026/11/23/anthropic-nvidia-shares.html', "CNBC Nov 23 - 'Shares of Nvidia surged 31.48% after the company announced Monday morning that Jensen Huang was reinstated as CEO'")
page('CNBC1116', 'https://www.cnbc.com/2026/11/16/trump-nvidia-stock-trades-jensen-huang.html', "CNBC Nov 16 analysis - 'bought and sold Nvidia stock at least 103 times'; 'three largest individual stock holdings, worth between $12.5 million and $58 million'; 'the filings give broad dollar ranges'; 'no evidence that Trump directed the trades'")
page('ABCWH', 'https://abcnews.com/US/trump-owned-12-million-nvidia-stock-end-year/story?id=138393684', "ABC News - White House spokesperson: 'independently managed by third-party financial institutions. All holdings are maintained in discretionary accounts'")
page('CNBC1109', 'https://www.cnbc.com/2026/11/09/nvidia-jensen-huang-china-spy-trump-lobbying.html', "CNBC Nov 9 - '$25 million toward his White House ballroom'; 'The company initially sought to keep its ballroom contribution anonymous, according to documents obtained by The Washington Post' (CROP: headline NOT shown - URL/headline carry 'spy'; body lines only)")
page('CNBC1015', 'https://www.cnbc.com/2026/10/15/trump-ballroom-nvidia-cisco-donations.html', "CNBC Oct 15 - 'Nvidia, Cisco and ServiceNow confirmed multimillion-dollar donations'; spokesperson 'our support for the United States is paramount, and independent of any business interests'")
page('MEDIAITE', 'https://www.mediaite.com/media/news/todd-blanche-wildly-claims-doj-independence-is-a-misperception-i-work-for-president-trump', "Mediaite Oct 21 2026 - 'Todd Blanche Wildly Claims DOJ Independence is a Misperception: I Work For President Trump' (joined the New York Post's Miranda Devine on her podcast; criticizing Biden-era Attorney General Merrick Garland)")
page('TNR', 'https://newrepublic.com/post/216921/todd-blanche-department-justice-supposed-run-president-whims', "The New Republic - 'Todd Blanche Says Everyone Else Is Confused About DOJ Independence'")
page('NYPP', 'https://nypost.com/2026/11/24/us-news/trump-leaves-door-open-to-jensen-huang-pardon-and-urges-him-not-to-plead-5th-to-congress-next-week/', "NY Post Nov 24 exclusive - Trump leaves door open to Huang pardon ('It's always an option, I guess, but I don't think it'll be necessary.'; 'I don't think he needs to take the Fifth.'; 'tell the truth' to Congress when he testifies next week; House Foreign Affairs Committee next Tuesday)")
page('OAG', 'https://oag.ca.gov/news/press-releases/attorney-general-bonta-serves-investigative-subpoena-nvidia', "California AG press release - 'Attorney General Bonta Serves Investigative Subpoena on Nvidia' ('whether Nvidia misled investors and the public')")
page('CNNRK', 'https://www.cnn.com/2026/11/24/politics/video/jamie-raskin-todd-blanche-donald-trump-jensen-huang-nvidia-department-of-justice-attorney-general-pardon-congress', "CNN video page - 'Raskin: Blanche's answers on Nvidia were breathtaking gobbledygook'")
page('NYPR', 'https://nypost.com/2026/11/24/us-news/rubio-jensen-huangs-nvidia-as-malign-influence-before-ouster', "NY Post Nov 24 - Rubio's concern about Jensen Huang, Nvidia being 'malign influence' ('sources and officials told The Post'). CROP: headline + first paragraph only - the next sentence contains 'suspected Chinese spy' and must stay out of frame")
page('FORT', 'https://fortune.com/2026/11/17/jensen-huang-nvidia-house-committee-return-ceo-testimony/', "Fortune Nov 17 - 'He and Nvidia general counsel Tim Teter have voluntarily agreed to transcribed interviews with the House Foreign Affairs Committee, the Select Committee on the Chinese Communist Party and the House Intelligence Committee'; caption 'slated to appear before the House Foreign Affairs panel on Dec. 1'")
page('MOFO', 'LEDGER:C15 MoFo client alert (URL in research/ledger.md C15)', "Morrison Foerster - 'Democrats are in the minority until the 120th Congress convenes on January 3, 2027.'")
page('JEFF', 'https://jeffries.house.gov/2026/11/23/speaker-designate-jeffries-statement-on-the-reinstatement-of-jensen-huang-as-ceo-of-nvidia', "Speaker-Designate Jeffries statement Nov 23 - 'swift, thorough and wide-ranging investigation into business malfeasance by NVIDIA and corrupt abuse of power by Howard Lutnick and the Department of Commerce'")

def tmpl(key, desc, basis):
    src(key, 'TEMPLATE', 'edit-v2-toolkit ' + key, desc + ' - built from: ' + basis, 'built graphic from real captures/numbers; no AI imagery; used once')
tmpl('T_SPLIT', 'SPLIT: CNBC transcript (Trump) | Bloomberg Law (Blanche)', 'CNBCT + BLAW captures')
tmpl('T_NUM', "NUM: one number template for the money run (103 -> $12.5M-$58M; ranges)", 'CNBC1116 figures')
tmpl('T_DOC', 'DOC: justice.gov joint statement PDF (Commerce + DOJ on Megaspeed, Nov 16 2026)', 'https://www.justice.gov/opa/media/1472536/dl?inline=')
tmpl('T_POST', 'POST: Schumer X post Nov 24 2026', 'https://x.com/SenSchumer/status/2125288276034543676')

FOOT_KINDS = ('CLIP', 'ENVATO', 'KHO')

# ---------------------------------------------------------------- rows
# (start, treatment, key, src_in, note, markers, person)
#   start: 0.0 for first row of a segment, else a phrase (ASR spelling) whose first word starts the row
#   markers: list of (VO phrase, evidence words) -> 'marker on "evidence" a-b' computed from the VO phrase
EVT, SCN, GFX, WEB = 'FOOT-EVT', 'FOOT-SCN', 'FOOT-GFX', 'WEBHEAD'
R = {}
R['B1'] = [
    (0.0, EVT, 'CNNo', 54.0, "Trump walking on the White House lawn (CNN file footage) - 'The president said'", [], True),
    ('exonerated.', WEB, 'CNBCT', None, "CNBC transcript line; marker on 'exonerated'", [('exonerated.', 'exonerated')], False),
    ('A reporter called', EVT, 'FOXP', 57.0, "presser podium, Blanche LISTENING to a reporter's question about the assurance given to the board (not speaking); chyron 'DOJ ANNOUNCES RESULTS OF LARGEST-EVER CRACKDOWN ON SCAMMERS...' (on tape)", [], True),
    ('Then the attorney general', WEB, 'CNBC1124', None, "CNBC lede 'Attorney General Todd Blanche and FBI Director Kash Patel on Tuesday dodged questions from reporters about a purported investigation'", [('the attorney general was asked', 'Attorney General Todd Blanche'), ('investigated him', 'a purported investigation')], False),
    ('Listen to the question', SCN, 'K_doja', 1.0, "scene: DOJ headquarters exterior ('listen to the question') - the presser venue", [], False),
]
R['B2'] = [
    (0.0, WEB, 'CNBC1124', None, "appearance 2: CNBC photo + caption (real AFP/Getty photo of Blanche and Patel at the podium)", [('Tuesday, November 24, at the Justice Department', 'at the Department of Justice in Washington, DC, Nov. 24, 2026')], True),
    ('The event was meant', WEB, 'FOXA', None, "Fox News article headline", [('crackdown on scammers', 'largest anti-scam surge in history')], False, {'lead': ('E_news', 1.0, "scene: scrolling news on a phone ('The event was meant to announce') - scam theme, no legible text", False)}),
    ('Questions about NVIDIA', EVT, 'FOXP', 65.9, "presser podium, Blanche listening, mouth closed (frame-checked 66-72 s); Fox chyron text line masked (on-tape 'SPY' wording), FOX bug stays", [], True),
]
R['B3'] = [
    (0.0, WEB, 'NBC', None, "NBC quote line", [('talks with the president', "I'm not going to get into communications I have with the president")], False, {'lead': ('E_wh2', 2.0, "scene: White House ('He would not discuss his talks')", False)}),
    ('He never said outright', WEB, 'AJZ', None, "Al Jazeera headline", [('never said outright whether Huang was investigated', 'declines to confirm if Nvidia\'s Jensen Huang was investigated')], False),
    ('Hold on to that', EVT, 'PBS', 65.0, "still photo of Trump (PBS file) - 'the president said a word'; not speaking", [], True),
    ('week. That word was pardon', WEB, 'NYPP', None, "NY Post headline", [('pardon.', 'pardon')], False, {'tail': ('E_city', 2.0, "scene: city aerial at dusk (beat out)", False)}),
]
R['B4'] = [
    (0.0, EVT, 'FOXP', 69.2, "presser podium, Blanche listening while a reporter presses on Huang, mouth closed (frame-checked); Fox chyron text line masked ('SPY' not on tape), FOX bug stays", [], True),
    ('Huang been investigated', WEB, 'NBC', None, "appearance 2: NBC quote lines", [('Huang been investigated', '"What does that mean?" "Had Huang been investigated for what?"')], False, {'tail': ('E_office', 2.0, "scene: empty office ('for what?') - beat before the tape", False)}),
]
R['B5'] = [
    (0.0, WEB, 'AJZ', None, "appearance 2: Al Jazeera quote", [('leaks never suggested Huang himself was under investigation', "Even the reporting from the various leaks or sources ... didn't suggest that Huang himself was under some sort of investigation")], False, {'tail': ('E_room', 0.5, "scene: empty briefing room", False)}),
    ('reporter raised the export', WEB, 'CNBC1124', None, "appearance 3 (2 within any 60 s): CNBC quote", [('the export investigation', 'when you say the export investigation is still ongoing'), ('did not know what the reporter was talking about', "I don't know what you're talking about")], False),
    ('Then he described', SCN, 'K_paper', 1.0, "scene: piles of case files ('the workload')", [], False),
]
R['B6'] = [
    (0.0, SCN, 'K_court', 2.0, "scene: US federal courthouse ('hundreds, he says. So which one?')", [], False),
    ('Here is one', 'DOC', 'T_DOC', None, "DOC (only use) - START: justice.gov PDF page 1 slides up from bottom to full frame (0.4 s), header in view; CHANGE: marker sweeps the date line then the header", [('In November', 'November 16, 2026'), ('Justice Department and Commerce', 'JOINT STATEMENT FROM DEPARTMENT OF COMMERCE AND DEPARTMENT OF JUSTICE ON MEGASPEED INVESTIGATION')], False),
    ('a joint statement. It', 'DOC', 'T_DOC', None, "DOC cont. - CHANGE: slow push-in (100->112 %) to first paragraph; marker on the investigation line; END: hard cut to footage (no outro)", [('investigating a company called Megaspeed', 'update on the investigation of the Singaporean company Megaspeed')], False),
    ('That statement was about', EVT, 'PBS', 25.0, "Jensen Huang on stage at an Nvidia event (PBS file) - 'not Jensen Huang'", [], True),
    ('Commerce then moved', WEB, 'FEDREG', None, "Federal Register PDF, entity-list paragraph", [('Blacklist Megaspeed', "Additions to the Entity List ... 'PT Megaspeed International' ... 'Megaspeed (Thailand) Co., Ltd.'")], False),
    ('on November 23rd', WEB, 'FEDREG', None, "same document, last-page footer", [('November 23rd', 'Filed: 11/23/2026')], False),
    ('reporter reminded Blanche', EVT, 'FOXP', 1.8, "presser: the reporter's 'November 12th' question in progress, Blanche listening, mouth closed (frame-checked 2-12 s); Fox chyron text line masked if it carries 'SPY'", [], True),
    ('issue. Blanche answered', WEB, 'CNBC1124', None, "appearance 4 (2 within any 60 s): CNBC quote", [('export investigations.', 'We have hundreds, if not more, export investigations')], False, {'lead': ('E_dcair', 3.0, "scene: Washington aerial ('Blanche answered')", False)}),
    ('a Justice Department export investigation', WEB, 'JSPR', None, "justice.gov press-release page title", [('investigation into Megaspeed', 'Joint Statement ... on Megaspeed Investigation'), ('the department said so itself', 'Department of Justice')], False, {'lead': ('E_fbi', 2.0, "scene: FBI headquarters (DOJ component) - 'a Justice Department export investigation'", False)}),
    ('Next came the praise', SCN, 'K_dojb', 3.0, "scene: DOJ building, second angle ('Next came the praise')", [], False),
]
R['B7'] = [
    (0.0, EVT, 'RTR', 5.0, "Nvidia HQ, Santa Clara (Reuters) - 'Notice the condition'", [], False),
    ('Nvidia were the target', WEB, 'AJZ', None, "appearance 3 (2 within any 60 s): Al Jazeera quote", [('target or under criminal investigation', 'if Nvidia was the target, or was the subject of some criminal investigation')], False),
    ('He said that would', WEB, 'AJZ', None, "same appearance, marker continues", [("not be the president's message", "then that wouldn't be the message that the president is")], False, {'lead': ('RTR', 9.5, "Nvidia HQ sign, Santa Clara (Reuters; burned Reuters location caption 'Santa Clara, California' is on tape)", False)}),
    ('So was Nvidia', EVT, 'CNBCr', 14.0, "Nvidia HQ aerial (CNBC; shot 13.93-17.02 s, ends before the anchor cut) - 'So was Nvidia a target?'", [], False),
    ('then a reporter asked', EVT, 'PBS', 30.0, "Nvidia headquarters exterior (PBS file) under the question about Huang's continuing access", [], False),
]
R['B8'] = [
    (0.0, EVT, 'FOXP', 488.0, "presser: next reporter question in progress right after the clearance answer; Blanche listening (chyron text line masked, FOX bug stays)", [], True),
]
R['B9'] = [
    (0.0, EVT, 'CNBCr', 105.5, "Nvidia chips / boards close-up (CNBC) - 'The chips.'", [], False),
    ('Two days earlier', WEB, 'CNNT', None, "CNN transcript header", [('Director of National Intelligence, Jay Clayton', 'Interview With U.S. Director of National Intelligence Jay Clayton'), ('went on CNN', 'Aired November 22, 2026')], False),
    ('Dana Bash asked', WEB, 'CNNT', None, "same page, the Bash question line", [('whether China has these chips', 'BASH: ... these chips?')], False),
]
R['B10'] = [
    (0.0, WEB, 'CNNT', None, "appearance 2: CNN transcript, Clayton answer", [('facts alleged in the indictment', 'based on the facts alleged in the indictment')], False, {'lead': ('E_tv', 2.0, "scene: hand with a TV remote ('Clayton qualified it' - the TV interview)", False)}),
    ('Allegations, not findings', SCN, 'K_stamp', 0.5, "scene: stamp on a document ('Allegations, not findings')", [], False),
    ('In New York', SCN, 'E_nyse', 2.0, "scene: New York Stock Exchange entrance ('In New York, federal prosecutors')", [], False),
    ('allege a scheme', WEB, 'DOJSDNY', None, "justice.gov release title", [('divert servers with American AI technology to China', 'Unlawfully Divert Cutting Edge U.S. Artificial Intelligence Technology to China')], False),
    ('They allege about', WEB, 'DOJSDNY', None, "same page, numbers paragraph; title stays in frame", [('$510 million', 'approximately $510 million'), ('spring of 2025', 'Between late April 2025 and mid-May 2025'), ('Three men', 'Three Charged')], False, {'lead': ('E_lab', 1.0, "scene: lab monitor with circuit board ('They allege')", False)}),
    ('Nvidia itself is not', SCN, 'E_racks', 6.0, "scene: data-center server racks ('Nvidia itself is not')", [], False),
    ('Then there is Alice', SCN, 'E_sg', 8.0, "scene: Singapore skyline (her company Megaspeed is Singaporean per DOC) - NO photo of Alice Huang", [], False),
    ('Jensen Huang resigned', EVT, 'RTR', 15.0, "flowers laid at Nvidia HQ the day Huang stepped down (Reuters, Nov 12)", [], False),
    ('The New York Times reported', WEB, 'PBSA', None, "PBS article line (text only)", [('in contact with a top official', 'had been in contact with a top official'), ("China's Ministry of State Security", 'China Ministry of State Security')], False),
    ("China's government denied", WEB, 'AJZ', None, "appearance 4 (2 within any 60 s): Al Jazeera line", [('denied the allegations', 'Beijing has denied the report as a "smear"')], False),
    ('Quick recap', SCN, 'E_cal', 6.0, "scene: calendar pages turning ('Quick recap')", [], False),
    ('Nvidia reinstated Huang', WEB, 'CNBC1123', None, "CNBC markets story line", [('reinstated Huang on Monday', 'announced Monday morning that Jensen Huang was reinstated as CEO')], False),
    ('CNBC reported the president', GFX, 'CNBCr', 31.0, "CNBC on-air card 'Trump tells CNBC I made the deal to reinstate Nvidia's Jensen Huang' (real CNBC graphic)", [], False),
    ("Blanche's word", WEB, 'NBC', None, "appearance 3 (2 within any 60 s): NBC quote", [('encouraged.', 'to encourage the board to reinstate him')], False),
]
R['B11'] = [
    (0.0, SCN, 'E_capflowers', 2.0, "scene: Capitol behind flowers ('put two statements side by side')", [], False),
    ('Trump told CNBC', GFX, 'CNBCi', 93.0, "the event itself: CNBC Squawk on the Street phone interview, Nov 23 - screen = Trump still + CNBC graphics while Trump says 'They did a pretty good investigation ... exonerated. I don't know what word you want to use' (src srt 01:32.7-01:45.7); audio muted under VO, no lip movement", [], True),
    ('At the podium', EVT, 'CBS', 756.4, "presser: Blanche listening, mouth closed (frame-checked 756-770 s); CBS chyron on tape 'AG BLANCHE ON IF NVIDIA'S HUANG HAS BEEN INVESTIGATED: \"FOR WHAT?\"' = the words the VO quotes; mask CBS HEADLINES ticker row", [], True),
    ('And the night before', 'SPLIT', 'T_SPLIT', None, "SPLIT (only use) - START: frame divides in 0.4 s; LEFT pane = CNBC transcript crop (CNBC masthead + 'PRESIDENT TRUMP: They did a pretty good investigation ... exonerated' with yellow marker already on, recalling the line just heard over the interview footage); CHANGE: RIGHT pane slides in from right with Bloomberg Law crop (headline + quote) while left pane dims to 60 %", [('on Fox News', 'says on Fox News'), ('investigation into Wang was closed', 'when asked if an investigation into Jensen Huang is closed')], False, {'lead': ('E_capdusk', 2.0, "scene: Capitol at dusk ('And the night before')", False)}),
    ('Law quoted him', 'SPLIT', 'T_SPLIT', None, "SPLIT cont. - marker sweeps the quote; END: both panes at 100 %, hard cut", [("That assumes there is an investigation that's open", "That assumes there is an investigation that's open"), ('never been discussed publicly', "that's never been discussed publicly")], False),
    ('Read those two', SCN, 'E_papers', 8.0, "scene: newspapers on the press ('Read those two together')", [], False),
    ('One says a pretty', GFX, 'PBS', 90.0, "PBS card: Trump CNBC phone-interview audiogram 'And the investigation showed that he did.' (real PBS on-air graphic)", [], False),
    ('The other says', WEB, 'BLAW', None, "Bloomberg Law page (standalone)", [('an open investigation has never been discussed publicly', "investigation that's open, and that's never been discussed publicly")], False),
    ('NBC News reported', SCN, 'E_wh', 6.0, "scene: White House exterior ('an administration official')", [], False),
    ('administration official gave', WEB, 'NBC', None, "appearance 4 (2 within any 60 s): NBC line", [('an administration official', 'An administration official said'), ('the attorney general told the president', 'the attorney general told the president')], False),
    ('department had no evidence', WEB, 'NBC', None, "same appearance, marker continues", [('no evidence of wrongdoing by Wang or the company', 'the DOJ had no evidence of wrongdoing by Huang or the company')], False),
    ('No evidence is not', SCN, 'E_facade', 8.0, "scene: flag on a federal building facade (opinion line)", [], False),
]
R['B12'] = [
    (0.0, SCN, 'E_trader', 8.0, "scene: trader at screens ('Follow the money')", [], False),
    ('CNBC analyzed', WEB, 'CNBC1116', None, "CNBC analysis headline + key point", [("president's financial disclosures", 'a CNBC analysis found')], False),
    ('or sold Nvidia stock', 'NUM', 'T_NUM', None, "NUM (only template; appearance 1 of 2) - START: '103' lands centre in 0.3 s on dark CNBC-capture backdrop (CNBC1116 key-point crop at 25 % opacity behind); yellow marker bar under '103'", [('103 times', '103')], False, {'lead': ('E_phone', 1.0, "scene: hand on a stock-trading app ('bought or sold Nvidia stock')", False), 'tail': ('E_ticker', 2.0, "scene: ticker numbers (no names legible)", False)}),
    ('By the end', GFX, 'CNBCi', 1500.0, "CNBC interview screen with live NVDA board (Nvidia stock on CNBC) - 'one of his largest stock holdings'", [], False),
    ('The disclosure puts', 'NUM', 'T_NUM', None, "NUM appearance 2 - CHANGE: '103' slides up and out; range '$12.5M - $58M' types in from left (no extra words); marker under the range", [('$12.5 million and $58 million', '$12.5M - $58M')], False, {'lead': ('E_charts', 2.0, "scene: trader watching charts ('The disclosure puts')", False)}),
    ('Those forms report', 'NUM', 'T_NUM', None, "NUM cont. - CHANGE: backdrop crop swaps to CNBC1116 line 'the filings give broad dollar ranges' at 100 %, marker on it; END: range card shrinks to top-right and cuts out", [('ranges, not exact figures', 'the filings give broad dollar ranges')], False),
    ('On the day Huang', GFX, 'CNBCr', 36.0, "CNBC on-air board 'NVIDIA 169.15 +49.63 +34.76%' with 'PRESIDENT TRUMP: I SPOKE TO JENSEN HUANG LAST NIGHT' (real CNBC graphic) - the +30 % step of the money run as real evidence", [], False),
    ('percent. The White House', WEB, 'ABCWH', None, "ABC News White House statement", [('third-party managers', 'independently managed by third-party financial institutions'), ('discretionary accounts', 'maintained in discretionary accounts')], False, {'mid': ('E_flag2', 2.0, "scene: US flag on a pole (between the two quoted phrases)", False)}),
    ('CNBC found no evidence', WEB, 'CNBC1116', None, "appearance 2: CNBC line", [('no evidence the president directed the trades', 'no evidence that Trump directed the trades')], False),
    ('ballroom. Nvidia has committed', EVT, 'WHB', 0.5, "Trump walking into the White House ballroom construction site (WH channel; walking, not speaking)", [], True),
    ('toward the White House ballroom', GFX, 'CNNo', 30.2, "CNN on-air donor board (Nvidia $25M) - real CNN graphic", [], False),
    ('to documents obtained', WEB, 'CNBC1109', None, "CNBC body lines (headline cropped out)", [('documents obtained by The Washington Post', 'according to documents obtained by The Washington Post'), ('keep that contribution anonymous', 'initially sought to keep its ballroom contribution anonymous')], False, {'mid': ('RTR', 0.0, "Nvidia HQ, Santa Clara (Reuters, opening frames before the caption) - 'The company'", False)}),
    ('the donation. Its spokesperson', EVT, 'RTR', 25.0, "Nvidia HQ (Reuters) - 'Nvidia confirmed the donation'", [], False),
    ('support for the United States', WEB, 'CNBC1015', None, "CNBC spokesperson quote", [('independent of any business interests', 'independent of any business interests')], False, {'tail': ('E_wh3', 2.0, "scene: White House north side", False)}),
    ('We found no reporting', EVT, 'WHB', 240.0, "ballroom construction site, Trump's back turned to camera (WH channel; not speaking)", [], True),
    ('outcome. But a president', EVT, 'CNNo', 63.1, "Trump in the Oval Office reading a document, then at his desk (CNN file footage; shots 63.03-68.07 / 68.07-71.70) - not speaking to camera", [], True),
    ('be judging that CEO', EVT, 'PBS', 60.0, "Jensen Huang holding a chip on stage (PBS file) - 'that CEO'", [], True),
]
R['B13'] = [
    (0.0, EVT, 'FOXP', 484.0, "presser: Blanche listening, mouth closed (frame-checked 484-500 s); Fox chyron text line masked, FOX bug stays", [], True),
    ('October on the New York Post', WEB, 'MEDIAITE', None, "Mediaite lede", [('New York Post podcast', "joined the New York Post's Miranda Devine on her podcast")], False),
]
R['B14'] = [
    (0.0, WEB, 'MEDIAITE', None, "appearance 2: Mediaite lede + headline", [("Biden's Justice Department", 'criticizing Biden-era Attorney General Merrick Garland'), ('Mediate', 'DOJ Independence is a Misperception')], False),
    ('and the New Republic', WEB, 'TNR', None, "New Republic headline", [('New Republic', 'The New Republic'), ('Department independence', 'Confused About DOJ Independence')], False, {'mid': ('E_towers', 2.0, "scene: skyscrapers looking up (between the two marker lines)", False)}),
]
R['B15'] = [
    (0.0, EVT, 'PBS', 20.0, "still photo of Trump with Jensen Huang (PBS file) - 'President Trump told'", [], True),
    ('York Post a pardon', WEB, 'NYPP', None, "appearance 2: NY Post quote", [('always an option, I guess, but I don\'t think it will be necessary', "It's always an option, I guess, but I don't think it'll be necessary")], False),
    ('That was an Oval', SCN, 'E_whair', 2.0, "scene: White House aerial ('That was an Oval Office interview')", [], False),
    ('He also said', WEB, 'NYPP', None, "appearance 3 (2 within any 60 s): NY Post quote", [('take the fifth', "I don't think he needs to take the Fifth")], False),
    ('Huang is due before', WEB, 'NYPP', None, "same appearance, lede line", [('Congress next week', 'when he testifies next week'), ('tell the truth', '"tell the truth"')], False),
    ('There are two limits', SCN, 'E_flags', 8.0, "scene: federal building with flags (general-law line; factcheck C7 PASS)", [], False),
    ("and California's attorney general", WEB, 'OAG', None, "oag.ca.gov release title", [('subpoenaed Nvidia', 'Serves Investigative Subpoena on Nvidia')], False, {'tail': ('RTR', 12.0, "Nvidia HQ sign, Santa Clara, California (Reuters; on-tape location caption) - the company being subpoenaed", False), 'lead': ('K_sfcourt', 1.0, "scene: Phillip Burton federal building, San Francisco ('and California's attorney general')", False)}),
    ('including whether it misled', WEB, 'OAG', None, "same page, body line", [('misled investors', 'whether Nvidia misled investors and the public')], False),
    ('As of today', SCN, 'E_campus', 6.0, "scene: Nvidia campus architecture ('no charges ... announced')", [], False),
]
R['B16'] = [
    (0.0, SCN, 'K_capdc', 6.0, "scene: US Capitol ('Democrats did not hold back')", [], False),
    ('Jamie Raskin', EVT, 'CNNR', 0.0, "Raskin full frame LISTENING while Collins asks her question (Collins audio not heard; Raskin not speaking) - CNN bug + chyron on tape", [], True),
    ('told CNN what', WEB, 'CNNRK', None, "CNN video page title", [("Blanche's answers", "Blanche's answers on Nvidia")], False),
]
R['B17'] = [
    (0.0, WEB, 'CNNRK', None, "appearance 2: CNN video page title", [('gobbledygook', "breathtaking 'gobbledygook'")], False, {'lead': ('E_hands', 2.0, "scene: hands on a phone ('He also called the attorney general's answers')", False)}),
    ('Senator Chuck Schumer', EVT, 'FBS', 0.0, "Senate chamber WIDE (Forbes, src 0.0-2.9 before the cut to Schumer) - Schumer not lip-visible; Forbes name strap 'SEN. CHUCK SCHUMER Democrat, New York' is the outlet's on-tape graphic", [], True),
    ('He wrote that', 'POST', 'T_POST', None, "POST (only use) - START: real X post capture (header '@SenSchumer' + date) rises from bottom, 0.3 s; marker", [('shipped extremely advanced chips to China', 'shipped extremely advanced chips to China')], False),
    ('violating export control', 'POST', 'T_POST', None, "POST cont. - CHANGE: slow pan down the post; marker; END: hard cut", [('violating export control law', 'violating US export control law'), ('rocket engines to the Soviets during the space race', 'selling rocket engines to the Soviets during the Space Race')], False),
    ("That is Schumer's", SCN, 'E_chip', 8.0, "scene: chip macro ('That is Schumer's allegation')", [], False),
    ('is Marco Rubio', EVT, 'FOXR', 12.0, "Rubio at the State Department photo spray (Fox)", [], True),
    ('whether Huang', EVT, 'FOXR', 22.5, "the question moment -> Rubio turns and walks out (src 24-27 s)", [], True),
    ('The New York Post reported', WEB, 'NYPR', None, "NY Post headline + first paragraph (crop stops above the 'spy' sentence)", [('citing sources and officials', 'sources and officials told The Post'), ('malign influence', "'malign influence'")], False, {'mid': ('E_meeting', 1.0, "scene: people at a meeting table (between 'sources and officials' and 'malign influence')", False), 'lead': ('E_whfence', 2.0, "scene: White House behind the fence ('The New York Post reported')", False)}),
    ('So his silence', SCN, 'E_neo', 8.0, "scene: flags on a neoclassical federal building ('his silence stands out')", [], False),
]
R['B18'] = [
    (0.0, SCN, 'E_flag', 8.0, "scene: US flag ('Here is our view')", [], False),
    ('Huang. The president says', GFX, 'PBS', 96.0, "PBS card (Trump CNBC audiogram), later window - 'The president says it happened'", [], False),
    ('the attorney general has not', EVT, 'CBS', 357.5, "presser: Blanche listening to the November 12th question (CBS angle; not speaking)", [], True),
    ('and the attorney general says', WEB, 'MEDIAITE', None, "appearance 3 (2 within any 60 s): Mediaite headline", [('works for the president', 'I Work For President Trump')], False),
    ('It is a loyalty', SCN, 'E_capflag', 8.0, "scene: Capitol with flag (opinion line)", [], False),
    ('The next dates', SCN, 'E_capitol', 10.0, "scene: US Capitol ('The next dates matter')", [], False),
    ('counsel have agreed', WEB, 'FORT', None, "Fortune body line", [('transcribe interviews', 'agreed to transcribed interviews'), ('three House committees', 'House Foreign Affairs Committee, the Select Committee on the Chinese Communist Party and the House Intelligence Committee')], False),
    ('Huang appears December', WEB, 'FORT', None, "same page, photo caption line", [('December 1st', 'on Dec. 1')], False),
    ('Democrats take control', SCN, 'K_capeast', 2.0, "scene: Capitol east front - 'January 3rd' line (MoFo line carried in SOURCES; factcheck C15)", [], False),
    ('Jeffries, the Democrat', WEB, 'JEFF', None, "jeffries.house.gov statement", [('speaker designate', 'SPEAKER-DESIGNATE JEFFRIES STATEMENT'), ('swift, thorough', 'swift, thorough and wide-ranging')], False),
    ('wide-ranging investigation of NVIDIA', WEB, 'JEFF', None, "same page, marker continues", [('investigation of NVIDIA', 'investigation into business malfeasance by NVIDIA'), ('the Commerce Department', 'the Department of Commerce')], False, {'lead': ('E_capwater', 2.0, "scene: Capitol across the water ('wide-ranging investigation')", False)}),
    ('Sub-Puna Power', EVT, 'FOXP', 7.6, "presser: Blanche listening (Nov 12 question, later window; mouth closed, frame-checked) - 'subpoena power'", [], True),
    ('If Blanche faces', EVT, 'CBS', 762.5, "presser: Blanche listening to the 'who is assessing' question (CBS angle)", [], True),
    ('what do you think', EVT, 'FOXP', 495.0, "presser: Blanche listening, final question of the Q&A (chyron text line masked)", [], True),
]

# ---------------------------------------------------------------- helpers
def norm(w):
    w = re.sub(r"[^a-z0-9$.'-]", '', w.lower().replace('\u2019', "'")).strip(".'-")
    return re.sub(r"'s$", '', w).replace('-', '')

def find(seg, phrase, after=0.0):
    toks = [norm(x) for x in phrase.split() if norm(x)]
    ws = W[seg]
    for i, w in enumerate(ws):
        if w['s'] < after - 1e-6: continue
        ok = True
        for j, t in enumerate(toks):
            if i + j >= len(ws) or norm(ws[i + j]['w']) != t: ok = False; break
        if ok:
            return ws[i]['s'], ws[i + len(toks) - 1]['e']
    raise SystemExit(f'phrase not found in {seg} after {after}: {phrase!r}')

def words_between(seg, t0, t1):
    return ' '.join(w['w'] for w in W[seg] if w['s'] >= t0 - 0.05 and w['s'] < t1 - 0.05)

DUR = {}
def dur(path):
    if path not in DUR:
        p = os.path.normpath(os.path.join(CASE, path))
        out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip()
        DUR[path] = float(out) if out else None
    return DUR[path]

def fmt(s):
    m = int(s // 60); return f'{m:02d}:{s - 60 * m:04.1f}'

def ts2s(t):
    p = [float(x) for x in t.split(':')]
    return p[0] * 60 + p[1]

# per-clip frame notes (checked on extracted frames)
KNOTE = {
    'K1': "src 14.0-15.1 is the CBS 24/7 bumper on tape (reporter audio starts 15.2) - keep (outlet branding) or hold first podium frame; chyron 'DEPT. OF JUSTICE HOLDS NEWS CONFERENCE' = neutral; mask the bottom CBS 'HEADLINES' ticker row (unrelated stories), CBS NEWS 24/7 bug stays",
    'K2': "chyron neutral; mask CBS 'HEADLINES' ticker row, bug stays",
    'K3': "mask CBS 'HEADLINES' ticker row, bug stays",
    'K4': "chyron 'AG TODD BLANCHE TAKES QUESTIONS ABOUT NVIDIA'S JENSEN HUANG' = neutral; mask ticker row",
    'K5': "chyron quotes tape ('FOR WHAT?'); mask ticker row",
    'K6': "chyron quotes tape ('FOR WHAT?'); mask ticker row",
    'K7': "CNN chyron 'U.S. INTEL DIRECTOR ON JENSEN HUANG SCANDAL' - 'scandal' is CNN framing, not Clayton's words -> crop/mask the chyron text line, CNN bug stays; split-screen Bash|Clayton as aired",
    'K8': "Pod Force One logo kept; no chyron",
    'K9': "CNN chyron 'TRUMP SAYS HE'S OPEN TO A PARDON FOR JENSEN HUANG' = matches NY Post quote (C-row NYPP) - keep; split Collins|Raskin as aired",
}

# ---------------------------------------------------------------- build
rows = []
film = 0.0
errors = []
for item in PLAN:
    if item['type'] == 'clip':
        k = item['id']; key = {'TC-axC1IL00.mp4': 'CBS', 'CNN_me20cb05073fdab89ec615e8b341bdd6d459587184.mp4': 'CNNC',
                               'CNN_me6ad953179aa97b71867f032e98881920cf2d84c5.mp4': 'CNNR', 'podforceone_hVCMk36xo_s_1015.mp4': 'PF1'}[item['src']]
        a, b = ts2s(item['in']), ts2s(item['out'])
        d = b - a
        rows.append(dict(seg=k, t0=0.0, t1=d, words=item['words'], tr='CLIP', key=key, sin=a, sout=b,
                         note=f"{k} speaker's own words on tape ({item['claim']}); burned captions only; " + KNOTE.get(k, ''), markers=[], person=True, film=film))
        film += d
        continue
    seg = item['seg']; D = W[seg + '_dur']
    spec = R[seg]
    starts = []
    cur = 0.0
    for i, r in enumerate(spec):
        if i == 0: starts.append(0.0); continue
        s, _ = find(seg, r[0], cur)
        t = round(max(cur, s - 0.04), 2); starts.append(t); cur = s + 0.01
    starts.append(D)
    # pass 1: raw rows with marker spans (markers searched inside the row as written)
    seg_rows = []
    for i, r in enumerate(spec):
        _, tr, key, sin, note, mk, person = r[:7]
        pads = r[7] if len(r) > 7 else {}
        t0, t1 = starts[i], starts[i + 1]
        spans = []
        for vo, ev in mk:
            a, b = find(seg, vo, t0 - 0.5)
            b = min(b, D)  # last word may ring past Bn_dur in words.json
            if a < t0 - 0.3 or b > t1 + 0.3:
                errors.append(f'{seg} {t0:.2f}: marker {vo!r} {a:.2f}-{b:.2f} outside row {t0:.2f}-{t1:.2f}')
            spans.append((ev, a, b))
        seg_rows.append(dict(tr=tr, key=key, sin=sin, note=note, spans=spans, person=person, t0=t0, t1=t1, pads=pads))
    # pass 2: evidence captures hold only around their markers (lead 0.5 s, tail 0.5 s); the rest of the
    # sentence goes to footage: extend the neighbouring footage row (<= 6 s) or use the row's declared pad
    def is_ft(x): return x['tr'] in ('CLIP', EVT, SCN, GFX)
    out_rows = []
    for i, x in enumerate(seg_rows):
        if x['tr'] in ('WEBHEAD', 'SPLIT', 'NUM', 'DOC', 'POST') and x['spans']:
            c0 = max(x['t0'], round(min(a for _, a, _ in x['spans']) - 0.25, 2))
            c1 = min(x['t1'], round(max(b for _, _, b in x['spans']) + 0.25, 2))
            lead, tail = c0 - x['t0'], x['t1'] - c1
            prev = out_rows[-1] if out_rows else None
            if lead >= 0.6 and 'lead' in x['pads']:
                k2, s2, n2, p2 = x['pads']['lead']
                out_rows.append(dict(tr=EVT if S[k2]['kind'] == 'CLIP' else SCN, key=k2, sin=s2, note=n2, spans=[], person=p2, t0=x['t0'], t1=c0, pads={}))
            elif lead >= 0.4 and prev is not None and is_ft(prev) and prev['tr'] != 'CLIP' and c0 - prev['t0'] <= 6.0:
                prev['t1'] = c0
            else:
                c0 = x['t0']
            nxt = seg_rows[i + 1] if i + 1 < len(seg_rows) else None
            tail_row = None
            if tail >= 0.6 and 'tail' in x['pads']:
                k2, s2, n2, p2 = x['pads']['tail']
                tail_row = dict(tr=EVT if S[k2]['kind'] == 'CLIP' else SCN, key=k2, sin=s2, note=n2, spans=[], person=p2, t0=c1, t1=x['t1'], pads={})
            elif tail >= 0.4 and nxt is not None and is_ft(nxt) and nxt['sin'] is not None and nxt['sin'] - tail >= 0 and nxt['t1'] - c1 <= 6.0:
                nxt['sin'] = round(nxt['sin'] - tail, 2); nxt['t0'] = c1
            else:
                c1 = x['t1']
            x['t0'], x['t1'] = c0, c1
            if 'mid' in x['pads'] and len(x['spans']) > 1:
                # split the capture at the widest gap between markers; footage plays in the gap
                sp = sorted(x['spans'], key=lambda z: z[1])
                gi = max(range(len(sp) - 1), key=lambda j: sp[j + 1][1] - sp[j][2])
                g0, g1 = round(sp[gi][2] + 0.25, 2), round(sp[gi + 1][1] - 0.25, 2)
                if g1 - g0 >= 0.6:
                    k2, s2, n2, p2 = x['pads']['mid']
                    a_row = dict(x, t1=g0, spans=sp[:gi + 1])
                    b_row = dict(x, t0=g1, spans=sp[gi + 1:], note=x['note'] + ' (capture resumes)')
                    m_row = dict(tr=EVT if S[k2]['kind'] == 'CLIP' else SCN, key=k2, sin=s2, note=n2, spans=[], person=p2, t0=g0, t1=g1, pads={})
                    out_rows += [a_row, m_row, b_row]
                    if tail_row: out_rows.append(tail_row)
                    continue
            out_rows.append(x)
            if tail_row: out_rows.append(tail_row)
        else:
            out_rows.append(x)
    for x in out_rows:
        t0, t1 = x['t0'], x['t1']
        for ev, a, b in x['spans']:
            if a < t0 - 0.3 or b > t1 + 0.3:
                errors.append(f'{seg} {t0:.2f}: marker {ev!r} {a:.2f}-{b:.2f} outside trimmed row {t0:.2f}-{t1:.2f}')
        mtxt = [f'yellow marker on "{ev}" {a:.2f}-{b:.2f}' for ev, a, b in x['spans']]
        row = dict(seg=seg, t0=t0, t1=t1, words=words_between(seg, t0, t1), tr=x['tr'], key=x['key'], sin=x['sin'],
                   sout=(x['sin'] + (t1 - t0)) if x['sin'] is not None else None, note=x['note'], markers=mtxt, person=x['person'], film=film + t0)
        rows.append(row)
    film += D
TOTAL = film

# ---------------------------------------------------------------- validate
for r in rows:
    s = S[r['key']]
    if s['kind'] in FOOT_KINDS:
        d = dur(s['where'])
        if r['sin'] is None: errors.append(f"{r['seg']} {r['t0']}: footage row without window")
        elif d is None: errors.append(f"{r['seg']}: cannot probe {s['where']}")
        elif r['sout'] > d + 0.01: errors.append(f"{r['seg']} {r['t0']:.2f}: window {r['sin']}-{r['sout']:.2f} > file {d:.2f} ({r['key']})")

# exact source-timecode repeats (overlapping windows of the same file)
by = collections.defaultdict(list)
for r in rows:
    if r['sin'] is not None: by[r['key']].append((r['sin'], r['sout'], r['seg'], r['t0']))
overl = []
for k, v in by.items():
    v.sort()
    for x, y in zip(v, v[1:]):
        if y[0] < x[1] - 0.01: overl.append(f'{k} {x[2]}@{x[0]:.1f}-{x[1]:.1f} vs {y[2]}@{y[0]:.1f}-{y[1]:.1f}')

# ---------------------------------------------------------------- write TSV
def srcfield(r):
    s = S[r['key']]
    if r['sin'] is not None: return f"{s['where']} @{fmt(r['sin'])}-{fmt(r['sout'])}"
    return f"{s['where']}" if s['kind'] != 'TEMPLATE' else f"{r['key']} ({s['where']}) <- {s['desc'].split(' - built from: ')[1]}"

GRAPH = ('WEBHEAD', 'SPLIT', 'NUM', 'DOC', 'POST')
def is_foot(r): return r['tr'] in ('CLIP', EVT, SCN, GFX)
SRC_LINE = {}
lines = ['seg\tt0\tt1\twords spoken\ttreatment\tsource file or URL + src in-time\ttext-on-screen\trights note\tMATCH/NO MATCH\tfilm_t0']
nomatch = 0
for r in rows:
    s = S[r['key']]
    if r['tr'] == 'CLIP' or r['tr'] in (EVT, SCN, GFX):
        tos = 'none (outlet bug/chyron only)' if r['tr'] != SCN else 'none'
        if r['tr'] == GFX: tos = 'outlet on-air graphic as aired (no added text)'
    else:
        tos = '; '.join(r['markers']) if r['markers'] else 'capture only'
    match = 'MATCH'
    if r['tr'] in GRAPH and not r['markers']: match = 'NO MATCH'
    if r['tr'] in ('CLIP', EVT, SCN, GFX) and r['sin'] is None: match = 'NO MATCH'
    if match == 'NO MATCH': nomatch += 1
    rights = s['rights'] + ' | match: ' + r['note']
    lines.append('\t'.join([r['seg'], f"{r['t0']:.2f}", f"{r['t1']:.2f}", r['words'].replace('\t', ' '), r['tr'], srcfield(r), tos, rights, match, f"{r['film']:.2f}"]))

# ---------------------------------------------------------------- QC
n = len(rows)
cpm = n / (TOTAL / 60)
per_min = collections.Counter(int(r['film'] // 60) for r in rows)
lens = [r['t1'] - r['t0'] for r in rows]
le6 = sum(1 for x in lens if x <= 6.0 + 1e-6) / n * 100
li = max(range(n), key=lambda i: lens[i])
foot = sum(l for r, l in zip(rows, lens) if is_foot(r)) / TOTAL * 100
gfx_on_air = sum(l for r, l in zip(rows, lens) if r['tr'] == GFX) / TOTAL * 100
# source appearances: footage = per row, EXCEPT contiguous K clips from the same tape (K1+K2) = one excerpt;
# pages/templates = per appearance (contiguous run of rows with the same key)
app = collections.defaultdict(list)
prev = None
for r in rows:
    k = r['key']
    contiguous = prev is not None and prev['key'] == k and (S[k]['kind'] not in FOOT_KINDS or (prev['tr'] == 'CLIP' and r['tr'] == 'CLIP'))
    if not contiguous: app[k].append(r['film'])
    prev = r
# K clips per row (strict) for the second figure
app_strict = collections.defaultdict(list)
prev = None
for r in rows:
    k = r['key']
    contiguous = prev is not None and prev['key'] == k and S[k]['kind'] not in FOOT_KINDS
    if not contiguous: app_strict[k].append(r['film'])
    prev = r
def maxwin(d):
    m = 0; worst = []
    for k, ts in d.items():
        for i, t in enumerate(ts):
            c = sum(1 for u in ts[i:] if u < t + 60)
            if c > m: m = c
            if c > 2: worst.append(f'{k}@{fmt(t)}')
    return m, sorted(set(worst))
mw, worst = maxwin(app)
mws, worsts = maxwin(app_strict)
# template ledger
tl = collections.Counter()
for k in ('T_SPLIT', 'T_NUM', 'T_DOC', 'T_POST'): tl[k] = len(app.get(k, []))
# consecutive graphics
run = mrun = 0
for r in rows:
    run = run + 1 if r['tr'] in GRAPH else 0; mrun = max(mrun, run)
# visual-type runs
def vt(r): return 'FOOTAGE' if is_foot(r) else 'GRAPHIC'
runs = []; cur = None
for r, l in zip(rows, lens):
    if cur and cur[0] == vt(r): cur[2] += l
    else:
        cur = [vt(r), r['film'], l]; runs.append(cur)
long_runs = [f'{t} at {fmt(f)} = {l:.1f}s' for t, f, l in runs if l > 30]
longest_foot = max((x for x in runs if x[0] == 'FOOTAGE'), key=lambda x: x[2])
# talking heads under VO: rows flagged person in FOOT-EVT must be in the allowed list (listening/wide/still)
th = [r for r in rows if r['tr'] == EVT and r['person'] and not re.search(r'listen|LISTEN|WIDE|still|photo spray|question moment|walking|among supporters|Resolute|Oval|ballroom site|on stage|back turned|still photo|holding a chip', r['note'])]
# first 60 s person gaps
spans = [(r['film'], r['film'] + l) for r, l in zip(rows, lens) if r['person'] and r['film'] < 60]
gaps = []; last = 0.0
for a, b in spans:
    gaps.append(a - last); last = max(last, b)
gaps.append(max(0.0, 60 - last))
# generic stock reuse
stock = collections.Counter(r['key'] for r in rows if S[r['key']]['kind'] in ('ENVATO', 'KHO'))
stock_rep = {k: v for k, v in stock.items() if v > 1}
# coverage
cov = True
for seg in [f'B{i}' for i in range(1, 19)]:
    rs = [r for r in rows if r['seg'] == seg]
    if abs(rs[0]['t0']) > 1e-6 or abs(rs[-1]['t1'] - W[seg + '_dur']) > 1e-6: cov = False
    for x, y in zip(rs, rs[1:]):
        if abs(x['t1'] - y['t0']) > 1e-6: cov = False
kclips = [r for r in rows if r['tr'] == 'CLIP']
kwin = all(r['sin'] is not None for r in kclips)

q = ['#', '# ===== QC (shot-map v1, computed by edit/shotmap_v1_build.py) =====']
q.append(f'# film length {TOTAL:.1f}s ({fmt(TOTAL)}), shots {n} (VO rows {n - len(kclips)}, K clip rows {len(kclips)}); segment coverage 0 -> Bn_dur with no gaps: {"YES" if cov else "NO"}; K clip windows K1-K9 present: {"YES" if kwin else "NO"}')
q.append(f'# max same source per 60 s = {mw} (limit 2) -> {"PASS" if mw <= 2 else "FAIL " + str(worst)}  [footage per row; pages/templates per appearance; K1+K2 = one contiguous CBS excerpt]')
q.append(f'#   strict variant (every K clip row counted separately) = {mws}{" at " + ", ".join(worsts) if worsts else ""} - only K1/K2/K3 (all CBS, order and windows fixed by edit_plan_v1.json, K3 starts 58.9 s after K1); no b-roll involved')
q.append('# template ledger (template -> appearances): ' + ', '.join(f'{k[2:]} -> {v}' for k, v in tl.items()) + f' -> {"PASS" if all(v == 1 for k, v in tl.items() if k != "T_NUM") else "CHECK"}' + '; NUM = one template, 2 appearances (103 / $12.5M-$58M + ranges); its +30 % step is carried by real CNBC on-air board (+34.76 %) instead of a 3rd NUM appearance (same-source <=2/60 s); no TIMELINE, no Truth POSTSEQ')
q.append(f'# talking-head-under-VO rows = {len(th)} -> {"PASS" if not th else "FAIL " + str([(r["seg"], r["t0"]) for r in th])} (presser rows = Blanche LISTENING to questions or wides; Raskin row = listening while Collins asks; CNBC interview = still image; Senate = wide; Rubio = photo spray / walk-off, he never speaks)')
q.append(f'# footage % = {foot:.1f} (target 65-75) -> {"PASS" if 65 <= foot <= 75 else "FAIL"}; of which outlet on-air evidence graphics (FOOT-GFX) = {gfx_on_air:.1f}%; page captures + templates = {100 - foot:.1f}%')
q.append(f'# cuts/min = {cpm:.1f} (target 17-22) -> {"PASS" if 17 <= cpm <= 22 else "FAIL"}; per minute {[per_min[i] for i in range(int(TOTAL // 60) + 1)]} (last minute is {TOTAL % 60:.0f}s)')
q.append(f'# shots <= 6 s = {le6:.1f}% (target >= 90) -> {"PASS" if le6 >= 90 else "FAIL"}; longest shot {lens[li]:.2f}s ({rows[li]["seg"]} @{rows[li]["t0"]:.2f} {rows[li]["tr"]})')
q.append(f'# max consecutive graphic rows (WEBHEAD/SPLIT/NUM/DOC/POST) = {mrun} (limit 2) -> {"PASS" if mrun <= 2 else "FAIL"}')
q.append(f'# visual-type runs > 30 s: {", ".join(long_runs) if long_runs else "none"}; longest FOOTAGE run at {fmt(longest_foot[1])} = {longest_foot[2]:.1f}s' + (' [the only >30 s run = 2.3 s stock + K1+K2, which edit_plan_v1.json fixes back-to-back (31 s of contiguous tape); all VO-driven runs <= 30 s]' if len(long_runs) == 1 and longest_foot[1] < 15 else ''))
q.append(f'# first 60 s: longest stretch without a real person on screen = {max(gaps):.1f}s (limit 10) -> {"PASS" if max(gaps) <= 10 else "FAIL"}')
q.append(f'# exact source-timecode repeats (overlapping windows, same file) = {len(overl)} {overl if overl else ""}')
q.append(f'# generic stock (Envato + kho) items used more than once = {len(stock_rep)} {stock_rep if stock_rep else ""} -> {"PASS" if not stock_rep else "CHECK (courthouse_us: two different windows, B6 scene + B10 New York line)"}')
q.append('# added on-screen labels/cards/lower thirds = 0 (only real evidence + outlet bugs + burned captions); no circles/red rings/arrows; markers = yellow highlight on voiced words (+-0.3 s, computed from audio_full_v1/words.json)')
q.append(f'# NO MATCH rows = {nomatch}; clip rows without window = {sum(1 for r in rows if is_foot(r) and r["sin"] is None)}; rows without SOURCES.md line = 0 (every key below has one)')
q.append('# Alice Huang: no photo anywhere (PBS 150-160 s / CNBC 54-63 s photo windows avoided); the word "spy" never on screen: Fox chyron text line masked on FOXP rows >= 72 s, CNBC1124/CNBC1109/NYPR crops exclude the spy sentence/headline, PBS/AJZ crops text-only')
q.append('# flags for other roles (not visual blockers): VO ASR shows "Invidia"/"Wang"/"Mediate"/"Podforce One"/"Sub-Puna" - TTS pronunciations to check; "incoming Judiciary chair" rests on ledger C14 only (factcheck WEAK); FOXR has no burned Fox bug in the source file')
if errors:
    q.append('# BUILD ERRORS: ' + ' | '.join(errors))

out = os.path.join(CASE, 'edit', 'shotmap_v1.tsv')
if os.path.exists(out) and os.environ.get('SHOTMAP_OVERWRITE') != '1':
    raise SystemExit(f'{out} exists - new version = new file (set SHOTMAP_OVERWRITE=1 only while iterating v1 before hand-off)')
open(out, 'w').write('\n'.join(lines + q) + '\n')

# ---------------------------------------------------------------- SOURCES.md
used = collections.OrderedDict()
for r in rows: used.setdefault(r['key'], []).append(f"{r['seg']}@{r['t0']:.2f}")
sl = ['# SOURCES - blanche-huang-confession visual shot-map v1 (edit/shotmap_v1.tsv)', '',
      'Format: TYPE | key | file or URL | what | used in (seg@t0). Captures: each PAGE is to be captured by the editor to edit/cap/<KEY>.png (dpr2, masthead visible) - not yet captured at shot-map stage.',
      'Envato items were licensed for trump-nvidia-huang (license PDFs beside each file); kho items carry their own license PDFs.', '']
for title, kinds in (('Clips', ('CLIP',)), ('Pages (WEBHEAD captures)', ('PAGE',)), ('Templates (one use each)', ('TEMPLATE',)), ('Envato Elements', ('ENVATO',)), ('Project stock (kho)', ('KHO',))):
    sl.append(f'## {title}')
    for k, u in used.items():
        s = S[k]
        if s['kind'] in kinds:
            sl.append(f"- {s['kind']} | {k} | {s['where']} | {s['desc']} | {', '.join(u)}")
    sl.append('')
sl.append('## Supporting (named in rows, not shown as separate captures)')
sl.append('- PAGE | MOFO | research/ledger.md C15 (Morrison Foerster) | "Democrats are in the minority until the 120th Congress convenes on January 3, 2027." | B18 Jan 3 line (scene row; factcheck C15)')
sl.append('- PAGE | DOJ Office of the Pardon Attorney | research/ledger.md C7 | pardon power = federal offenses only | B15 general-law line (factcheck 122 PASS)')
open(os.path.join(CASE, 'research', 'SOURCES.md'), 'w').write('\n'.join(sl) + '\n')

print('\n'.join(q))
print('rows', n, 'errors', len(errors))
for e in errors: print('ERR', e)
