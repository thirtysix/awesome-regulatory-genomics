#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python vers. 3.12.3 ##########################################################
# Libraries ####################################################################
import os
import pandas as pd
from pathlib import Path
import re
################################################################################
# Description/Notes ############################################################
################################################################################
"""
PRESERVED ARTEFACT. This is the script that produced the dissertation table, kept
for provenance rather than for use.

The ONLY modification is redaction: the five absolute input/output paths, which
pointed at a local working directory, now read "<data-dir>/". Nothing else has
been touched, so the logic that produced the published table is verbatim: the
HTML stripping, the first-sentence rule with its e.g./i.e./etc./vs. guards, and
the set subtraction of the regulatory-element names from the TF names.

The script did not run as written even before redaction, because that working
directory no longer holds those files. See ../docs/provenance.md for the
field-by-field verification of the table it produced.
"""

################################################################################
# Base-level Functions #########################################################
################################################################################


################################################################################
# Task-specific Functions ######################################################
################################################################################


################################################################################
# Initiating Variables #########################################################
################################################################################
tf_results_fn = "<data-dir>/transcription_factor.results.tsv"
tf_results_df = pd.read_csv(tf_results_fn, sep="\t")

reg_elem_fn = "<data-dir>/reg_element_pred.results.tsv"
reg_elem_df = pd.read_csv(reg_elem_fn, sep="\t")

tf_results_unique_fn = "<data-dir>/transcription_factor.results_unique.tsv"
reg_elem_unique_fn = "<data-dir>/reg_element_pred.results_unique.tsv"
common_results_fn = "<data-dir>/common_results.tsv"
################################################################################
# Execution ####################################################################
################################################################################
tf_results_df['Title'] = tf_results_df['Title'].str.replace(r'<[^>]+>', '', regex=True)
reg_elem_df['Title'] = reg_elem_df['Title'].str.replace(r'<[^>]+>', '', regex=True)

##tf_results_df.insert(3, 'Description_short', [x.split(". ")[0] for x in tf_results_df['Description']])
##reg_elem_df.insert(3, 'Description_short', [x.split(". ")[0] for x in reg_elem_df['Description']])

tf_results_df.insert(3, 'Description_short', [re.split(r'(?<!e\.g)(?<!i\.e)(?<!etc)(?<!vs)\.\s+', x)[0] for x in tf_results_df['Description']])
reg_elem_df.insert(3, 'Description_short', [re.split(r'(?<!e\.g)(?<!i\.e)(?<!etc)(?<!vs)\.\s+', x)[0] for x in reg_elem_df['Description']])


reg_elem_names = reg_elem_df['Name'].tolist()
tf_names = tf_results_df['Name'].tolist()

tf_results_unique_df = tf_results_df[~tf_results_df['Name'].isin(reg_elem_names)]
tf_results_unique_df.to_csv(tf_results_unique_fn, sep="\t", index=False)

reg_elem_unique_df = reg_elem_df[~reg_elem_df['Name'].isin(tf_names)]
reg_elem_unique_df.to_csv(reg_elem_unique_fn, sep="\t", index=False)

common_names = [x for x in tf_names if x in reg_elem_names]
all_results_df = pd.concat([tf_results_df, reg_elem_df])
common_results_df = all_results_df[all_results_df['Name'].isin(common_names)]
common_results_df.to_csv(common_results_fn, sep="\t", index=False)
