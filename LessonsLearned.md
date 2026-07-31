# Lessons learned

Transferable lessons, not project trivia. `CLAUDE.md` holds the traps you need
before touching *this* code; this file holds the ones worth carrying to the next
project, and the reasoning that produced them.

A lesson earns a place here when it changed how the work was done, not merely
what the answer was. Each entry says what was believed, what happened, and what
to do differently.

---

## An LLM stage that reads its own output has no provenance

**Believed:** the `was:` field in `llm_proposals.yaml` held the original text, so
any rewrite could be audited or reverted.

**Happened:** the describe stage read `data/catalog.json`, which `build.py` had
already merged the previous run's rewrite into. The second run rewrote a rewrite.
For 1,407 of 1,563 records `was:` held generation 1, not the source. Nothing
crashed, nothing oscillated, no test failed - the only symptom was a provenance
field that quietly meant something other than what it said, and a handoff note
repeating the reassurance.

**Do differently:** before trusting any provenance field, diff it against the
actual raw source on a sample. Make derived stages read the raw input, so a
re-run is an *independent* derivation and agreeing with the existing value is
real corroboration rather than an echo.

## Feed a model a source it is documented not to trust, and it will use it

**Believed:** giving the describe prompt each record's EDAM annotations was free
extra context.

**Happened:** where the prose source was a fragment - 223 records had under 80
characters - the model padded the sentence out of those tags, which this project
documents at length as unreliable. A HiChIP peak caller was described as using
"an essential dynamics algorithm", a protein molecular-dynamics technique present
only as a wrong annotation. 23% of descriptions carried a claim traceable to a
tag alone.

**Do differently:** if a source is known-unreliable, say so *in the prompt* and
forbid it as a sole basis. Give the model a licence to abstain, because a plain
registry sentence beats a confident invention. And when the input is too thin to
answer from, find a better input rather than a better prompt - here, the tool's
own paper, which 90% of records had sitting in an API response already fetched
and discarded.

## Keep the whole response, not the fields you need today

**Happened:** `openalex_lookup()` fetched complete work objects and kept four
fields. The abstracts were arriving and being thrown away on every run. Getting
them back meant a second pass over 2,231 identifiers against a metered daily
budget, for data already paid for.

**Do differently:** persist whole API responses when the request is already made
and the quota is the scarce thing. Gzip made this 41 MB instead of 130 MB, which
is not a reason to discard anything. Keep any backfill behind an explicit flag:
a cached value short-circuits before the network, so folding a re-fetch into the
normal run is a surprise sweep that spends the day's allowance.

## A stated limit is not the limit that binds

**Believed:** descriptions were terse because the prompt capped them at 22 words.

**Happened:** actual output was median 11, maximum 19, and 96 fell *below* the
stated 8-word floor. Nothing ever approached the ceiling. What governed length
was "one sentence" plus a terseness instruction; the number was decorative.

**Do differently:** measure the distribution before tuning a limit. If nothing is
near the boundary, the boundary is not the cause.

## Cached is not the same as deterministic

**Happened:** re-running the describe stage with a small prompt addition changed
1,121 of 1,631 descriptions. The committed cache is what makes builds
reproducible, not the generation process.

**Do differently:** when asked whether generated content is reproducible, answer
precisely. "Cached and reproducible from committed data" is true and defensible;
"deterministic" is not. Also: cache keys that cover *inputs* but not the *prompt*
silently return stale answers when the prompt changes. Version the key and bump
it on every prompt edit.

## Both identifiers can be wrong together

**Believed:** where a record states both a PMID and a DOI, they are independent
witnesses, so comparing them catches a mistyped one. PMIDs are dense sequential
integers, so a typo lands on another real paper and every "does it resolve" check
passes; a DOI typo 404s loudly.

**Happened:** the observation about density is right and the conclusion drawn
from it was wrong. NOBAI carried a PMID one digit off its real one, resolving to
"Ellipsoidal particles at fluid interfaces" and taking that paper's 146 citations
against a true 15 - and the record carried the matching *physics DOI* too. The
DOI had evidently been populated from the bad PMID. They agreed, so the
cross-check stayed silent on the one case that motivated it.

**Do differently:** before relying on two fields agreeing, establish that they
were produced independently. Derived fields corroborate rather than check. The
only signal that caught this was semantic: does the paper's subject matter match
the tool's.

## A better description is a better audit

**Happened:** rewriting descriptions to say plainly what each tool does turned
into a scope audit for free. "Curates T-cell receptor sequences with cognate
antigens" is obviously not a regulatory-genomics tool; the vague text it replaced
was not obviously anything. 250 records admitted on a single unreliable
annotation were then found out of scope, including cell-image segmentation and
peptide toxicity prediction.

**Do differently:** expect quality work on one field to expose problems in
another, and leave room in the plan for it. The same pattern had already occurred
here once, when real citation counts exposed three out-of-scope records in the
top 15.

## Report the detector's blind spot with its results

**Happened:** three detectors built this session were each weaker than they first
appeared. Name-overlap between tool and paper title flagged 100 records, all
correct, because method papers routinely have descriptive titles. An alien-venue
scan flagged 12, all legitimate chemistry-journal methods papers. The PMID/DOI
cross-check could not see the case it was built for.

**Do differently:** state what a check cannot see, next to what it found. A rate
reported without its blind spot reads as coverage. Put a known-positive control
in any sweep and abort rather than report a number when the control fails - a
sweep whose control fails measures nothing.

## A rejected method may be right for a narrower problem

**Believed:** searching for a tool's paper by name was settled as forbidden. It
had put a text-matching library in the catalog under `Match`, so the rule was
"ask the tool, never the literature", and I defended it when challenged.

**Happened:** correct as a default, wrong as an absolute. Asked to fix 61 records
carrying a demonstrably wrong paper, the authoritative route resolved 8 and left
53 declaring nothing - mostly older tools whose pages are gone. A method that
leaves 87% unresolved is not a solution for that set. And the original failure
was not "name search"; it was **name search with nothing to verify against**.
These records now carry good descriptions, so a candidate can be adjudicated
against one, which closes precisely that hole. Asked about a tool called EP3, the
adjudicator answered that every candidate described the prostaglandin E receptor
rather than software - the `Match` failure, correctly refused.

**Do differently:** when rejecting a method, record *why* it failed, not just
that it did. A ban stated as a rule outlives the conditions that justified it. Re-
examine whether those conditions still hold before applying it to a new problem,
and check what the accepted method actually achieves on that problem rather than
assuming it suffices. Reinstate the method as a lower tier with the missing
safeguard attached, not as an equal.

## Guard against a fix that is worse than the bug

**Happened:** the search route proposed Signac's bioRxiv preprint at 164
citations to replace its Nature Methods paper at 1,889 - a swap this catalog had
already made once and documented. The candidate was correct in that it genuinely
describes the tool; it was simply the worse copy of the truth.

**Do differently:** a proposed correction needs a comparison against what it
replaces, not only a check that it is plausible on its own. Encode the known
direction of quality - published over preprint, higher citation count, real venue
- and mark anything moving the wrong way rather than trusting the judgement that
produced the candidate.

## Count the false positives before reporting a detector's yield

**Believed:** the `paper_matches` check, validated on NOBAI as a control pair and
producing plausible reasons, had found 61 records carrying the wrong paper. That
is how it was reported.

**Happened:** the user hand-checked four of the top hits. **Three were wrong.**
PINTS, NRL and asSeq all had the correct paper already; only EP3 was a real error,
pointing at a benchmark of promoter predictors instead of its own Genome Research
paper. A 75% false-positive rate on the sample, against a headline that implied 61
errors.

The cause is domain-specific and worth naming: **in genomics a tool usually ships
inside its biology or method paper.** NRLcalc is introduced in the methods of
"CTCF-dependent chromatin boundaries formed by asymmetric nucleosome arrays";
asSeq implements the method in "A statistical framework for eQTL mapping using
RNA-seq data", which names no software at all. A detector asking "is this abstract
about the tool" reads the normal case as a mismatch. One instruction made it
worse: telling the model that a benchmark comparing many tools is not the tool's
own paper is what sank PINTS, whose paper is a comparison that introduces it.

**Do differently:** a control pair proves a detector *can* fire correctly, not that
its hits *are* correct. Before reporting a count, hand-check a sample of the
positives and report the rate. Say "a review queue of 61 with an unmeasured false-
positive rate", never "61 errors". And when a check fires on a pattern, ask whether
that pattern is normal in the domain before treating it as a signal.

## Ask the thing itself, never search for its name

**Standing rule, re-confirmed:** to find or verify a tool's paper, read what the
tool declares - its Bioconductor citation page, `CITATION.cff`, `codemeta.json`,
README, homepage. Never search the literature by name. Tool names in this field
are short and collide across all of software: `Match` resolved to a text-matching
library, `SEA` to an RPC framework. The same method that finds a missing paper
finds a wrong one, by deriving independently and comparing.
