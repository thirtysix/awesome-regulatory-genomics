"""Staged re-audit of scope exclusions made under the old prompt.

Calibrated first: the same 22 items answered identically across three passes,
so a change of verdict is the prompt fix rather than the model wobbling.

Every flip gets a second opinion from GLM-5 - a real one. The original
decisions cite agreement between V4-Flash and V3.1-Terminus, and Terminus is a
silent alias for V4-Flash, so that agreement never happened.
"""
import sys, os, json, gzip, yaml, pathlib
sys.path.insert(0, "pipeline")
from llm_assist import SCOPE_AUDIT_SYSTEM, call, parse_json, paper_context

SP = "/tmp/claude-1000/-home-harl-Dropbox-manuscripts-000-dissertation/c784b26e-f6a9-42a5-8654-fdc7719f8789/scratchpad"
STATE = pathlib.Path(f"{SP}/reaudit_state.json")
key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN")
BULK, SECOND = "deepseek-ai/DeepSeek-V4-Flash", "zai-org/GLM-5"

prop = yaml.safe_load(open("curation/llm_proposals.yaml").read()) or {}
sets = {k: (prop.get(k) or {}) for k in ("admitted_out_of_scope", "out_of_scope_confirmed", "majority_out_of_scope")}
sel = json.load(gzip.open("data/raw/selected.json.gz", "rt"))
sel = sel["list"] if isinstance(sel, dict) and "list" in sel else sel
selby = {e["biotoolsID"]: e for e in sel if e.get("biotoolsID")}

def prompt(bid, rec):
    t = selby.get(bid) or {}
    try: paper = paper_context(t) if t else {}
    except Exception: paper = {}
    topics = [x.get("term","") if isinstance(x,dict) else str(x) for x in (t.get("topic") or [])][:6]
    lines = [f"Name: {t.get('name', bid)}",
             f"Catalog description: {t.get('description') or rec.get('description') or '(none)'}",
             f"EDAM operations (unreliable): {', '.join(t.get('_operations') or []) or 'none'}",
             f"EDAM topics: {', '.join(topics) or 'none'}",
             f"Admitted by rule: {rec.get('admitted_by','?')}"]
    if paper.get("title"): lines.append(f"Paper title: {paper['title']}")
    if paper.get("abstract"): lines.append(f"Paper abstract: {paper['abstract'][:1200]}")
    return "\n".join(lines)

def ask(model, bid, rec):
    txt, cost, _ = call(model, SCOPE_AUDIT_SYSTEM, prompt(bid, rec), key, max_tokens=300)
    return (parse_json(txt) or {}), cost

state = json.loads(STATE.read_text()) if STATE.exists() else {"done": {}, "cost": 0.0}
todo = [(s, b) for s in sets for b in sorted(sets[s]) if f"{s}/{b}" not in state["done"]]
batch = int(sys.argv[1]) if len(sys.argv) > 1 else 25
work = todo[:batch]
print(f"batch of {len(work)}; {len(todo)} remaining of {sum(len(v) for v in sets.values())} total\n", flush=True)

flips = []
for setname, bid in work:
    rec = sets[setname][bid]
    try:
        got, c = ask(BULK, bid, rec); state["cost"] += c
    except Exception as e:
        print(f"  ERR {bid[:24]} {type(e).__name__}", flush=True); continue
    ins = got.get("in_scope")
    entry = {"set": setname, "bulk": ins, "bulk_reason": str(got.get("reason"))[:200]}
    if ins is True:
        try:
            got2, c2 = ask(SECOND, bid, rec); state["cost"] += c2
            entry["second"] = got2.get("in_scope"); entry["second_reason"] = str(got2.get("reason"))[:200]
        except Exception as e:
            entry["second"] = "err"; entry["second_reason"] = type(e).__name__
        flips.append((bid, entry))
        mark = "BOTH AGREE" if entry.get("second") is True else "split"
        print(f"  FLIP [{mark:10s}] {bid[:24]:26s} {entry['bulk_reason'][:64]}", flush=True)
    state["done"][f"{setname}/{bid}"] = entry
STATE.write_text(json.dumps(state, indent=1))
d = state["done"]
tot_flip = sum(1 for v in d.values() if v["bulk"] is True)
both = sum(1 for v in d.values() if v["bulk"] is True and v.get("second") is True)
print(f"\n  this batch: {len(flips)} flips of {len(work)}")
print(f"  cumulative: {len(d)} audited, {tot_flip} flipped by the bulk model, {both} confirmed by GLM-5")
print(f"  spend so far: ${state['cost']:.4f}")
