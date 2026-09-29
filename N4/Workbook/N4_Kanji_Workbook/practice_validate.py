"""Generic per-world practice-bank validator (reusable, Worlds 1-14 + mock).
Usage: python practice_validate.py <bank.json>
Gates: cumulative in-pool scope, 5/4/3/1/2 split, 3-4-4-4 answers (no 3-run),
all chapter kanji covered <=2x, answer-key completeness, opener variety, register watch.
"""
import json, io, sys, re, os
from collections import Counter, defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Portable: derive the project root from this file's location (Workbook/..) instead of a
# hard-coded absolute path, so the embedded QA package runs on any machine.
WORKBOOK_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(WORKBOOK_DIR, "..", ".."))
bank_path = sys.argv[1] if len(sys.argv) > 1 else r"w1_bank.json"
if not os.path.exists(bank_path):                       # clean rc 2, no traceback (TC-QA03)
    print("BLOCKED: bank file not found:", bank_path); sys.exit(2)
b = json.load(open(bank_path, encoding="utf-8"))
W = b["world"]  # 1-indexed; 0 = cumulative mock (any of the 143 kanji)
MOCK = (W == 0)

# cumulative allowed pool = kanji from Worlds 1..W  UNION  N5-prerequisite set
kj = json.load(open(os.path.join(BASE, "data", "kanji.json"), encoding="utf-8"))
ent = kj["entries"]; ent.sort(key=lambda e: e["lesson_order"])
# World membership pinned to match build_kanji_book.py: the first 143 keep the original even
# 12-world split (12 per world; world 12 = 11 kanji); the 27 Kanshudo-N4 additions
# (lesson_order 144-170) go to appended worlds 13 (144-157) & 14 (158-170). 1-indexed here.
def _world_of(lo):
    return min((lo - 1) // 12, 11) + 1 if lo <= 143 else 13 + (lo - 144) // 14
world_of = {e["glyph"]: _world_of(e["lesson_order"]) for e in ent}
cur = set(k for k, w in world_of.items() if w == W)          # this chapter's kanji
cum = set(world_of) if MOCK else set(k for k, w in world_of.items() if w <= W)
rd = json.load(open(os.path.join(BASE, "data", "n4_kanji_readings.json"), encoding="utf-8"))
n5 = set(k for k, v in rd.items() if v.get("tier") == "n5_prerequisite")
# Background kanji: not taught as headwords, but needed INSIDE a taught kanji's only natural N4 word
# and always shown with a reading. 可 is only teachable via 可能 / 許可, which need 能 / 許 (the same
# words already appear, with readings, on the 可 lesson page). Allowed as supporting kanji.
BACKGROUND = {"能", "許"}
allowed = cum | n5 | BACKGROUND
KRE = re.compile(r"[一-鿿]")
print("World %d: chapter kanji=%d, cumulative<=W=%d, +N5=%d -> allowed=%d"
      % (W, len(cur), len(cum), len(n5), len(allowed)))

rev = b["review"]; fails = []

def scope(qid, *texts):
    bad = set()
    for t in texts:
        seq = t if isinstance(t, list) else [t]
        for x in seq:
            bad |= {c for c in KRE.findall(x or "") if c not in allowed}
    if bad: fails.append("%s OUT-OF-SCOPE: %s" % (qid, " ".join(sorted(bad))))

for q in rev:
    scope(q["id"], q["sentence"], q["options"], q.get("underline", ""))
for k, ex in b["examples"].items():
    scope("REI-" + k, ex["sentence"], ex["options"], ex.get("underline", ""))

for q in rev:
    if len(q["options"]) != 4: fails.append("%s !=4 options" % q["id"])
    if not (1 <= q["correct"] <= 4): fails.append("%s bad correct" % q["id"])

tc = Counter(q["type"] for q in rev)
# Split relaxed 2026-07-22: 用法(usage) slots whose target kanji can't host a clean pure-lexical
# 問題5 item are reallocated to 問題1 reading (per language-review). Fixed anchors: 表記=4/6,
# 言い換え=1/5; reading absorbs former usage slots; usage may be 0..2 (chapter) / 0..5 (mock).
if MOCK:
    ok = (tc["orthography"] == 6 and tc["paraphrase"] == 5 and tc["usage"] <= 5
          and tc["kanji_reading"] >= 9 and sum(tc.values()) == 35)
else:
    ok = (tc["orthography"] == 4 and tc["paraphrase"] == 1 and tc["usage"] <= 2
          and tc["kanji_reading"] >= 5 and sum(tc.values()) == 15)
print("type counts:", dict(tc), "->", "OK" if ok else "MISMATCH")
if not ok: fails.append("type split mismatch")

seq = [q["correct"] for q in rev]; pc = Counter(seq)
run = max((len(list(g)) for _, g in __import__("itertools").groupby(seq)), default=0)
print("answers:", seq, "counts:", dict(sorted(pc.items())), "run:", run)
if run >= 3: fails.append("answer run >=3")
if any(pc.get(p, 0) == 0 for p in (1, 2, 3, 4)): fails.append("a position never occurs")
if pc and max(pc.values()) - min(pc.values()) > 1: fails.append("answer counts not 4/4/4/3")

if MOCK:
    distinct = len({k for q in rev for k in q["target_kanji"]})
    print("coverage: cumulative mock, %d distinct target kanji (no per-chapter cap)" % distinct)
else:
    tgt = Counter(k for q in rev for k in q["target_kanji"] if k in cur)
    missing = [k for k in b["world_kanji"] if tgt[k] == 0]
    over = [k for k, n in tgt.items() if n > 2]
    print("coverage:", {k: tgt[k] for k in b["world_kanji"]}, "| uncovered:", missing or "none", "| >2x:", over or "none")
    if missing: fails.append("uncovered: %s" % missing)
    if over: fails.append("over-2x: %s" % over)

ids = [q["id"] for q in rev]
if len(set(ids)) != len(ids): fails.append("dup ids")
sents = [q["sentence"] for q in rev if q["type"] != "usage"]
if len(set(sents)) != len(sents): fails.append("dup sentences")

for q in rev:
    if not (q.get("explanation") or "").strip(): fails.append("%s missing explanation" % q["id"])
    d = q.get("distractors", [])
    if len(d) != 4 or any(not (x or "").strip() for x in d):
        fails.append("%s needs a reason per option" % q["id"])

blocks = defaultdict(list)
for q in rev:
    if q["type"] == "usage": continue
    toks = q["sentence"].split()
    blocks[q["type"]].append(toks[0] if toks else q["sentence"])
for t, op in blocks.items():
    dup = sorted({o for o in op if op.count(o) > 1})
    if dup: fails.append("repeated opener in %s: %s" % (t, dup))
print("openers/block:", dict(blocks))

WATCH = ["会議", "業者", "課長", "部長", "社長", "残業", "契約", "出張", "給料", "会社"]
wh = [q["id"] + ":" + w for q in rev for w in WATCH if w in q["sentence"] + "".join(q["options"])]
print("register watch:", wh or "none")

# 10) 表記 real-word gate (JMdict): EVERY option of EVERY orthography (表記) item must be a
# real word (JMdict keb). Standing rule for the whole file: distractors are real kanji spellings
# of OTHER real words that are simply wrong here (ideally sharing a component with the target,
# e.g. 自分/気分/半分/十分, 問題/話題/主題), never invented non-words a student can eliminate on
# "that doesn't exist" grounds. Applies to single-kanji AND compound items alike.
import gzip
# Prefer the full JMdict cache; fall back to the bundled index (its keys are the real-word headwords
# among the bank tokens, so 表記-option membership is identical to the full cache); else SKIP.
JMD = os.path.join(BASE, "Workbook", "N4_Kanji_Workbook", "_refcache", "_jmdict_e.gz")
IDX = os.path.join(WORKBOOK_DIR, "_jmdict_index.json")   # bundled index sits next to this script
KEB = KSRC = None
if os.path.exists(JMD):
    KEB = set(re.findall(r"<keb>(.*?)</keb>", gzip.open(JMD, "rt", encoding="utf-8").read())); KSRC = "_jmdict_e.gz"
elif os.path.exists(IDX):
    KEB = set(json.load(open(IDX, encoding="utf-8")).keys()); KSRC = "_jmdict_index.json (bundled subset)"
if KEB is not None:
    for q in rev:
        if q["type"] != "orthography":
            continue
        nonwords = [o for o in q["options"] if o not in KEB]
        if nonwords:
            fails.append("%s 表記 has NON-WORD option(s): %s" % (q["id"], nonwords))
    print("JMdict real-word gate: applied to ALL 表記 options (keb=%d, source=%s)" % (len(KEB), KSRC))
else:
    print("JMdict real-word gate: SKIPPED (no cache or index)")

print("\n" + "=" * 50)
if fails:
    print("VALIDATION FAILED:")
    for f in fails: print("  -", f)
    sys.exit(1)
print("VALIDATION PASSED (World %d): scope, structure, distribution, coverage, answer-key, openers." % W)
