# Star Period Tool v2.3

Run INSTALL.bat once, put an observation table in UPLOAD_DATA_HERE, then run RUN.bat.

The complete application is MainC.py. Read [START_HERE.md](START_HERE.md) for the wizard, input formats and scientific limitations.

New in v2:

- Explicit unknown-period reconnaissance, approximate-period input in minutes/hours/days, or a manual continuous range.
- Separate before/after clipping panels; excluded observations are red.
- Individual method periodograms, enlarged peaks and final candidate periods in days/minutes.
- Optional Monte Carlo for each selected supported method, with trial count and error-model choice.
- Reports distinguish fixed-window conditional results from independent validation; no forced unique best method.

[VALIDATION.md](VALIDATION.md) describes the checks and their limits. A portable set of new tests is in TESTS/test_workflow.py; run `python TESTS/test_workflow.py` after installing requirements.

UPLOAD_DATA_HERE/CY_Aquarii.csv is the user-supplied ASAS-SN table, copied unchanged from AP17210606 (2).csv and identified as CY Aquarii by its owner. Files in EXAMPLES are synthetic demonstrations. No observations are downloaded from a star name.

Version 2.1 adds visible Enter-to-accept column suggestions. ASAS-SN magnitude and flux representations remain separate; ambiguous headers require explicit selection.

Version 2.2 adds ZIP export and Print / Save PDF controls at the bottom of each generated HTML report. Full results remain automatically saved in RESULTS. Earlier-stage downloads contain only files already generated; download again after completion for the complete run.

Version 2.3 keeps the latest successful result and removes older recognized result/search folders after verifying the new ZIP. Failed or interrupted runs do not trigger cleanup. Input tables are preserved. Save any older result ZIP outside RESULTS before a subsequent successful calculation, or use --keep-history.
