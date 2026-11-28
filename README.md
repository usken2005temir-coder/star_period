# Star Period Tool v2.3

The complete application and instructions are in [StarPeriodTool](StarPeriodTool/README.md).

1. Install Python 3.9 or later.
2. Open StarPeriodTool and run INSTALL.bat once.
3. Put observations in UPLOAD_DATA_HERE.
4. Run RUN.bat and follow the wizard.

See [START_HERE.md](StarPeriodTool/START_HERE.md) for search modes, optional Monte Carlo and interpretation. All application code is in MainC.py; external scientific libraries are installed separately.

Search and uncertainty results are conditional on the selected data, bounds and model assumptions; no universal best period is guaranteed.

Version 2.1 adds visible Enter-to-accept column suggestions. ASAS-SN magnitude and flux representations remain separate; ambiguous headers require explicit selection.

Version 2.2 adds ZIP export and Print / Save PDF controls at the bottom of each generated HTML report. Full results remain automatically saved in RESULTS. Earlier-stage downloads contain only files already generated; download again after completion for the complete run.

Version 2.3 keeps the latest successful result and removes older recognized result/search folders after verifying the new ZIP. Failed or interrupted runs do not trigger cleanup. Input tables are preserved. Save any older result ZIP outside RESULTS before a subsequent successful calculation, or use --keep-history.
