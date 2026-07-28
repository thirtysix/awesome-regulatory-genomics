# What this project is, in plain terms

## The problem

If you study how genes get switched on and off, there are thousands of software
tools you might use, scattered across twenty years of papers. Finding the right
one is genuinely hard: there is no good index, the obvious search terms return
the wrong things, and the field's own registry is patchy in ways that are not
obvious until you check.

This project builds a catalog of those tools that you can search, filter and
trust, and it rebuilds itself.

## The inputs

- **bio.tools**, a public registry of bioinformatics software. It is the main
  source, and it is imperfect in ways that shaped the whole design.
- **A hand-written list** of tools bio.tools does not include at all.
- **GitHub, PyPI, bioconda, Bioconductor, CRAN** for finding where a tool's
  source code actually lives.
- **Crossref and OpenAlex** for publications and how often they are cited.

## The output

A catalog of about 1,800 tools, published two ways: a readable list for people
browsing, and a searchable table for people looking for something specific. Plus
a set of honesty documents that record what the catalog is unsure about.

## The objective

Not "as many tools as possible". Two things matter more:

1. **Don't miss the obvious ones.** Measured, not asserted: a hand-written list
   of tools the field treats as standard is checked on every build.
2. **Don't say things that are wrong.** A wrong link looks exactly like a right
   one, so it misleads silently. Everything inferred is marked as inferred.

## The approach, and why it looks like this

**Search widely, then filter hard.** The registry's search is fuzzy text matching
rather than a proper lookup, so asking precisely gets you nothing. The pipeline
deliberately over-collects, then applies strict rules afterwards.

**Don't trust the labels.** The registry lets people tag tools with standard
categories, and those tags are frequently wrong: a well-known motif scanner is
filed under "Genotyping", a major database under "Data handling". So the rules
are tiered, and there is a fallback that reads the tool's own description when
the labels are useless.

**Show your working.** Every tool that was rejected is written to a file with the
reason. Anyone who thinks the boundary is wrong can argue with the evidence
rather than guessing at intent.

**Use judgement where rules are weak, but never silently.** Language models
categorise tools better than hand-written patterns do, so they are used for that,
with three guards: removing a tool needs two different models to agree, adding
one gets checked by a third, and everything is written to a review file rather
than applied straight to the catalog.

**Assume you are wrong somewhere.** The whole project is built on the
observation, repeatedly confirmed, that plausible-looking output nobody checks is
where errors live. Several were found this way, including a citation that was
invented outright and a repository link that pointed at a Flutter package.

## How it stays current

A scheduled job re-runs the whole thing monthly and opens a proposed change for
review rather than updating silently. Nothing reaches the published catalog
without a person looking at the difference.

## Where it came from

It started as a 148-row table in a doctoral dissertation. That table was
verified line by line, kept for citation, and then superseded: the original
approach missed roughly nine out of ten relevant tools, for reasons documented in
`docs/provenance.md`.
