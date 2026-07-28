# Provenance

This catalog grew out of a table in a doctoral dissertation on transcription-factor
binding site prediction. The original table and the scripts that produced it are
preserved in [`../dissertation/`](../dissertation/), because the dissertation
refers to them. The only edit anywhere in that directory is the redaction of
five absolute working-directory paths in `filter_results.001.py`; its logic is
verbatim. This page records how that table was derived, what was
verified, and what this catalog does differently.

## The original table

`dissertation/transcription_factor.results_unique.csv` holds 148 tools in six
columns (`Name`, `Homepage`, `Description_short`, `Year`, `Citations`, `Identifiers`),
tab-separated despite the `.csv` extension, sorted by citation count descending.

It was produced by this chain:

```
biotools_query.019.py --operation "Transcription factor binding site prediction" --all
    -> transcription_factor.results.tsv          214 tools
biotools_query.019.py --operation "Transcriptional regulatory element prediction" --all
    -> reg_element_pred.results.tsv              308 tools

filter_results.001.py
    strips HTML tags from Title
    derives Description_short as the first sentence, guarding against
      splitting on "e.g.", "i.e.", "etc.", "vs."
    set-subtracts by Name: tools in the TF set that are NOT in the
      regulatory-element set
    -> transcription_factor.results_unique.tsv   148 tools

    drop ToolType/Description/Title, sort by Citations desc, save as .csv
    -> transcription_factor.results_unique.csv
```

Citation counts came from OpenAlex, resolved per publication by PMID (falling
back to DOI) and summed across all publications linked to a tool.

### Verification

The published table was checked field by field against
`transcription_factor.results_unique.tsv`:

| Check | Result |
| --- | --- |
| Row count | 148 = 148 |
| Tool-name sets | identical |
| `Homepage` | 0 mismatches |
| `Description_short` | 0 mismatches |
| `Citations` | 0 mismatches |
| `Identifiers` | 0 mismatches |
| `Year` | same values; TSV carries a `1994.0` float artefact |
| Row order | published table re-sorted by `Citations` descending |

The derivation is confirmed. Two caveats worth recording:

- `filter_results.001.py` reads from `0.datasets_visualizations/bio_tools/`,
  a path that no longer holds those files, so it will not re-run as written.
- The table is defined by *subtraction*. "TFBS-prediction tools that are not
  also regulatory-element-prediction tools" removed 66 tools whose only offence
  was carrying both EDAM annotations. That boundary is an artefact of
  annotation practice, not of biology.

## What this catalog changes

The dissertation table answered a narrow question well. As a general resource it
had three recall problems, each measured before the pipeline was redesigned.

**1. Planned queries that were never run.** `terms.txt` lists eight EDAM terms;
three result sets exist and only one reached the table. `"Sequence motif
discovery"` is listed twice and was never queried; it alone would have found
HOMER, Weeder and ChIPMunk. A fourth result set of 241 motif tools was computed
and discarded; 208 of them appear nowhere in the final table.

**2. EDAM annotations in bio.tools are unreliable.** Of 85 canonical tools in
this field checked against the live API, 58 were missed by the original queries.
A substantial share of those are *in* bio.tools, filed under operations no
sensible query would target (each row re-verified against the live API on
2026-07-28):

| Tool | bio.tools ID | bio.tools operation |
| --- | --- | --- |
| HOCOMOCO | `hocomoco` | Data handling |
| SICER | `sicer` | Sequence contamination filtering |
| ChIP-Atlas | `chip-atlas` | Genome assembly, Genome visualisation |
| Cluster Buster | `cluster_buster` | Clustering, Document clustering |

**3. bio.tools does not index a large part of the field.** 32 of the 85 are
absent outright: the sequence-to-function deep-learning generation (DeepBind,
DeepSEA, Basset, Basenji, Enformer, DanQ, Sei, DeepSTARR), most digital
footprinting methods (HINT-ATAC, PIQ, Wellington, pyDNase, CENTIPEDE), and
several major motif databases (CIS-BP, TRRUST, footprintDB).

A fourth failure mode sits between 2 and 3, and it is the one most likely to
fool an audit. Widely used tools are sometimes absent as records in their own
right while a *different* tool holds the obvious name. There is no bio.tools
record for the MEME Suite's FIMO: the ID `fimo` belongs to FiMO, an unrelated
genotyping and normalisation tool, and the scanner itself exists only as one
function of the `meme_suite` record. Searching by name finds something, so the
gap reads as coverage. FIMO is therefore carried in `seeds.yaml`, and this is
the same collision the resolvers guard against everywhere else: a matching name
is necessary but never sufficient.

### Consequences for the design

- **Query wide, filter narrow.** bio.tools' `operation=` is a fuzzy text match,
  not an ontology lookup: `q="cis-regulatory"` returns 107 records, while the
  same query unquoted returns about 3,500, matching "cis" *or* "regulatory".
  Precision is therefore applied afterwards, against the annotations a record
  actually carries.
- **Tier the operations.** Seventeen specific terms admit a record on their own;
  five ambiguous ones (`Sequence motif recognition`, which bio.tools also applies
  to protein and RNA motifs) need a corroborating topic or text signal; and five
  that belong to another field are listed in `REJECTED_OPERATIONS`, never queried
  and never able to admit anything. `Peak detection` is the clearest case: of the
  204 records carrying it, roughly three in four are proteomics, metabolomics or
  NMR tools.
- **Keep a text escape hatch.** Matching name and description against domain
  patterns, gated on a plausible EDAM topic, recovers in-domain tools with no
  usable annotation at all (gcapc, Q, CCAT, MixChIP, ChIPanalyser).
- **Curate what automation cannot reach.** `curation/seeds.yaml` carries the
  tools bio.tools does not list.
- **Union, do not subtract.** Categories are multi-label, so a tool that is both
  a TFBS predictor and a regulatory-element predictor appears under both instead
  of being deleted.

## Relationship between the two

The dissertation table is **not** regenerated from this pipeline. It stands as
published and remains citable. This catalog supersedes it going forward; the
148 rows are a subset of what the catalog now contains.
