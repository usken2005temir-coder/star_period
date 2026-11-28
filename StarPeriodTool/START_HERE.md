# Star Period Tool - standalone research application

## Install and start (Windows)

1. Install Python 3.9 or later.
2. Run INSTALL.bat once. It creates .venv and installs requirements.txt.
3. Put one-star, one-band observation tables into UPLOAD_DATA_HERE.
4. Run RUN.bat. The application asks which table to use if several are present.
5. Enter an object label, signal type and time units. The label does NOT identify or download a star.
6. Press Enter to accept the displayed column suggestions, or type a different column name.
7. Choose residual clipping (3 sigma by default, 0 to disable), analysis mode and search strategy.
8. Review the search setup and then the before/after clipping plot. Return to the console to continue or stop.
9. Open RESULT.html in the new RESULTS/run_... directory. FINAL_PERIODS.csv lists leading and alternative periods in days and minutes.

All application code, including all mathematical methods and report generation, is embedded in MainC.py. External scientific libraries still need installation. Reports open locally in your browser; input data are not uploaded. The original input is preserved. After a successful complete analysis, older recognized result/search folders are removed; the latest run remains. Use --keep-history to retain history.

## Input formats and columns

Supported: comma-separated CSV, tab-separated TSV, whitespace TXT/DAT, extensionless two/three-column text and tabular FITS (.fits/.fit/.fts). XLS/XLSX and image FITS are not supported. Decimal separators must be points. Headerless columns must be time, signal, optionally error; the first row is retained. More than three headerless columns need headers.

Example:

```csv
time,mag,mag_err
2459000.123,12.31,0.02
2459000.145,12.28,0.03
2459000.178,12.24,0.02
```

These three rows illustrate the format only. At least 12 valid points and eight distinct times are required; scientific adequacy usually needs much more. Errors must be positive standard uncertainties in signal units. Omit an unknown error column; do not fill it with zeros. Invalid numeric rows and nonpositive errors are audited separately.

ASAS-SN-style tables can contain both mag and flux. The wizard suggests magnitude when there is exactly one recognizable magnitude column, and displays mag/mag_err explicitly. Press Enter to accept; selecting flux changes the suggested signal/error columns. Only one representation is analyzed:

- Magnitudes: signal type magnitude, time column hjd, signal column mag, error column mag_err, input time unit days.
- Flux: signal type flux, time column hjd, signal column flux, error column flux_err.

A mixed-camera table may have calibration offsets. The application does not automatically fit camera offsets, calibrate measurements, correct time standards or apply barycentric corrections. Use consistent calibration and time standards. Different photometric bands must not be silently combined; CLI --band selects a band.

## Analysis modes

1. Full mode: four base methods and a separately refined harmonic model with internal prediction checks. If Monte Carlo is enabled, also perform conditional injection/recovery comparison and joint-model resampling.
2. Four base methods only.
3. Lomb-Scargle only.
4. Multiharmonic Fourier regression only (not FFT; related to LS).
5. Phase Dispersion Minimization (PDM) only.
6. Weighted Wavelet Z-transform (WWZ) only.
7. Preprocessing only: save the clipping report and cleaned table, then stop.

Single-method mode applies to final analysis; clipping uses supported preliminary candidates among the selected methods. Use clipping 0 / --no-clip for strictly no preprocessing search.

## Search strategy: unknown, approximately known or manual

The former median-gap range proposals have been replaced. Sparse sampling does NOT impose a hard lower-period cutoff. All searches still require explicit finite bounds, and periods outside those bounds remain untested.

### 1. Unknown period: broad reconnaissance

Choose minutes, hours or days and explicit lower/upper bounds. The editable example is 20 minutes to half the observation baseline; this is an interface starting point, NOT a physical inference or a complete range for every star.

The broad stage scans the entire declared envelope with LS and H=2 harmonic regression on a uniform frequency grid with spacing at most 1/(10*T). It uses chunked fast calculations and rechecks selected peaks using exact chi-square fits. It retains up to five separated peaks from each model, then proposes windows within +/-4/T in frequency and half/double-frequency companions inside the declared envelope. Overlapping windows are merged. Detailed LS/Fourier/PDM/WWZ searches use a common resolved grid inside those windows; gaps are not searched by all four methods.

No hidden coarsening or cadence-based removal of short periods occurs. The scout grid limit is 5,000,000 frequencies; the detailed grid limit is 200,000. Exceeding a limit produces an explanation. Narrow explicit bounds or deliberately change CLI limits. Grid counts are not runtime guarantees. WWZ and repeated simulations can be expensive.

IMPORTANT: this is a screening-and-refinement pipeline, not an exhaustive four-method global search. LS/H=2 screening can miss signals favored by other methods. Windows are selected on the same full observations. Internal folds, later method comparisons and Monte Carlo hold these windows fixed, so they are CONDITIONAL and not independent confirmation of the broad selection. A validated unique method winner is not declared in this mode. LS false-alarm probability is not reported for data-selected windows.

The scout plots use a peak-preserving display envelope, not every evaluated frequency. Candidate values are rechecked exactly. Inspect alternatives, harmonics and observing-window diagnostics; they do not automatically identify which peak is physical. A window maximum at a frequency difference only flags a possible alias relationship.

### 2. Approximately known period

Enter the approximate value, its unit (for example minutes), and a relative half-width in percent. The application records this prior information and searches the selected neighborhood. For example 89 minutes with +/-2% means 87.22 to 90.78 minutes. This is verification around prior information, not blind discovery. If the continuous grid is too large, the wizard offers to screen that SAME envelope first; accepting makes subsequent analysis data-selected and conditional.

### 3. Manual continuous range

Enter explicit bounds and units. Every selected method scans the same continuous resolved grid. No preliminary scout-window selection occurs. Inspect boundary peaks and broaden the range when justified. Long periods covering fewer than two cycles can resemble trends.

Exposure duration is optional and in seconds. Leave blank if unknown. A warning appears if a proposed short period is below twice the exposure duration. This convention is not a strict detection limit; exposure integration is not corrected.

## Clipping and the red points

The input plot shown during search setup is BEFORE clipping. It cannot yet label rejected measurements. After clipping, PREPROCESSING.html and sigma_clipping_result.png show TWO panels: the original valid measurements and retained (blue) / excluded (red) points. The search-setup page copied into the run also receives this clipping result.

The tool performs one conservative residual-clipping pass. A preliminary period search predicts the variable signal; a point must be flagged by every supported selected candidate model. The scale uses residual median absolute deviation and supplied errors. If more than 10% would be excluded or too few points would remain, clipping is skipped. Real extrema are not automatically treated as bad measurements. No arbitrary rejection is forced: if nothing is excluded, the report explicitly says so and there are no red observations.

Base-method periodograms, phase curves and measurement Monte Carlo use retained data. The separate joint model and internal recommendation protocol use original valid data before clipping; they are labelled accordingly. Red points are therefore excluded from base-method estimates, but not from that separate original-data check. No automatic flux-to-magnitude conversion or trend subtraction is performed.

Exports:

- source_input.*: exact input snapshot.
- valid_data_before_clipping.csv: valid original observations.
- clean_data.csv: retained observations.
- outliers.csv: flagged candidates for review, not proven instrumental defects.
- excluded_rows.csv: invalid input rows.
- preprocessing.json / PREPROCESSING.md: counts, threshold, scopes and time units.

Clean exports restore the original epoch and time unit. They retain time, signal, optional error and signal label. For subsequent V/R component-error propagation, use the original component table. If reusing an already cleaned table, choose clipping 0 to avoid another pass.

## Optional Monte Carlo for each method

The wizard asks y/n and the number of repetitions. Default is OFF. When enabled, every selected supported base method repeats its search over the ENTIRE selected frequency grid after independent Gaussian perturbation of the measurements. The same random draws are shared across methods. A method without a supported original peak is explicitly marked unavailable; no fake estimate is generated.

Supplied magnitude/flux errors or explicitly propagated V/R errors set perturbation scales. Without errors, the user must explicitly opt into a difference-MAD noise estimate or leave measurement Monte Carlo disabled. That empirical scale can include actual stellar variability and is not measured instrumental uncertainty. Fits remain equally weighted when no measurement errors are supplied.

Outputs: monte_carlo_summary.csv, perturbation_periods.csv, METHOD_monte_carlo.png and MONTE_CARLO.md. The report includes valid repetitions, failures, same-peak fraction and percentile summaries. Same-peak fractions use ALL requested trials as denominator. Global percentiles may span distinct aliases. Within-peak percentiles are conditional and must be read with recovery fractions. These are not calibrated confidence intervals, not a false-alarm probability and not proof that the period is correct.

Clipping, selected windows and fixed base harmonic counts are NOT recomputed in these repetitions. Broad screening is not repeated. Monte Carlo therefore does not quantify missed alternatives outside selected windows or the entire selection uncertainty. Ten repetitions are a quick functional check, not a scientific uncertainty estimate; 100+ are useful for exploration but do not remove model limitations.

With full mode and Monte Carlo enabled, the separate joint model also runs residual-block simulations and the recommendation procedure runs injection/recovery. With wizard Monte Carlo OFF, these simulation-based additions are disabled; internal deterministic fitting/prediction checks remain. CLI advanced resampling is separately controlled by --uncertainty-trials.

## Results

Open RESULT.html. At the top, leading method candidates and any refined joint modes are shown in days and minutes. FINAL_PERIODS.csv also includes up to three candidates from each base method. Alternatives are not automatically separate independent modes. No universal or forced unique best period is claimed; different method statistics are not directly comparable.

- METHOD_periodogram.png: one periodogram per selected method with the leading candidate marked; PDM prefers MINIMA, the others maxima.
- METHOD_peak_details.png: enlarged views of up to three peaks, with periods in minutes.
- phase_curves.png: retained observations folded at method candidates.
- sampling_window.png: finite-grid observing-window diagnostic, not a proof of aliasing.
- periodograms.csv / top_candidates.csv: full selected-grid numerical results.
- scout_candidates.csv / scout_periodograms.png / scout_alias_diagnostics.csv: reconnaissance evidence when used.
- range_advice.json / RANGE_ADVICE.html: exact search selection, input checksum, prior and limits.
- FINAL_RESULT.json / START_RESULT.md: candidate summary and comparison status.
- advanced.md / joint_periods.csv / joint_fit.png: separate original-data harmonic model and its limitations.
- run.json / tool_manifest.json / error_audit.csv: settings, numerical outputs, code/input hashes and error provenance.

Supplied errors weight LS, Fourier and joint fits by inverse variance. PDM is unweighted; WWZ uses temporal weights. WWZ may have insufficient local support for short periods in sparse surveys even if LS/PDM can recover a candidate; changing the display cannot create missing information. V/R periods describe spectroscopic intensity-ratio variability, not automatically stellar pulsation.

## Command line

Broad screen followed by a four-method comparison and 10 exploratory perturbations:

```powershell
python MainC.py --input UPLOAD_DATA_HERE/star.csv --time-col hjd --signal-col mag --error-col mag_err --signal-kind magnitude --min-period 0.02 --max-period 10 --discover --basic --bootstrap 10 --open-report
```

Explicit neighborhood, one method, no clipping or simulations:

```powershell
python MainC.py --input UPLOAD_DATA_HERE/star.csv --time-col hjd --signal-col mag --error-col mag_err --min-period 0.06 --max-period 0.063 --search-origin known --basic --methods ls --no-clip --bootstrap 0
```

Additional application switches: --step-by-step pauses after clipping; --preprocess-only stops after clipping; --open-report opens local HTML; --no-recommend disables simulation-based recommendation in full mode. Detailed numeric options are shown with --help. --manual prints this guide. --self-test checks a known synthetic period. No online data retrieval is performed.

UPLOAD_DATA_HERE/CY_Aquarii.csv contains the user-supplied ASAS-SN observations, copied unchanged from AP17210606 (2).csv and identified as CY Aquarii by its owner. It contains 413 rows with hjd, camera, mag, mag_err, flux and flux_err. Accept magnitude/hjd/mag/mag_err defaults to analyze magnitudes. EXAMPLES/synthetic_ratio.csv is synthetic with a true period of 0.7 days. Object labels are not independently resolved by the program.

## Scientific references

- Astropy Lomb-Scargle: https://docs.astropy.org/en/stable/timeseries/lombscargle.html
- VanderPlas (2018), Understanding the Lomb-Scargle Periodogram: https://doi.org/10.3847/1538-4365/aab766
- Stellingwerf (1978), PDM: https://doi.org/10.1086/156444
- Foster (1996), WWZ: https://doi.org/10.1086/118137
- SciPy least-squares refinement: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html
- NIST uncertainty propagation: https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-law-propagation-uncertainty

This is a research tool, not a completed thesis or proof of universal period accuracy.

## v2.1: Enter accepts visible input suggestions

The wizard reads headers before asking about columns. It displays suggested signal type, time column, signal column and matching error column. For hjd/camera/mag/mag_err/flux/flux_err tables, defaults are magnitude, days, hjd, mag, mag_err. Magnitude preference is shown explicitly, not inferred to be scientifically superior. Multiple magnitude bands or time columns are left unresolved for explicit selection. Generic time units cannot be inferred from numerical values; days is a visible default that must be checked. No error column is invented when errors are absent. The CLI remains strict about ambiguous columns.

## v2.2: Save buttons and result bundles

All reports are local files, not an online website. Every HTML page has a footer with Save all available results (ZIP) and Print / Save PDF. The ZIP is also stored as SAVE_RESULTS.zip in its results directory. It contains that directory's available reports, figures, tables, settings and source-input snapshot, if one has been saved. It does not contain all previous runs or the installed Python environment.

The search-setup archive contains only that stage. The preprocessing archive is refreshed after a stop or after final analysis completes. A ZIP downloaded before completion remains an earlier snapshot: download again from RESULT.html after completion for the full results. Each footer states its stage. Download location follows browser settings; a folder chooser is not guaranteed. Use the browser's save-link action if needed.

Extract the entire ZIP before opening RESULT.html (or PREPROCESSING.html for an incomplete run). Exported report copies keep their relative image/table links and replace ZIP controls with a saved-copy notice, avoiding recursive archives. PDF printing saves only the displayed page; use ZIP for all numerical results.

Existing old HTML reports are not modified automatically when replacing MainC.py. The new controls appear in newly generated reports.

## v2.3: Keep only the latest completed calculation

After the new RESULT.html and SAVE_RESULTS.zip have been saved and the ZIP verified, the program removes older recognized run/search folders in the SAME output directory. The newest calculation is retained. A failed, interrupted or preprocessing-only calculation does not trigger cleanup. Unknown directories, unfinished runs, newer concurrent runs and folders containing an active input/validation file are preserved. Symlink/junction targets are not traversed. Locked folders are reported rather than preventing access to the new result.

UPLOAD_DATA_HERE is not cleaned. Old result ZIPs located inside deleted run folders are deleted along with those runs. To keep a particular result, save/copy its ZIP OUTSIDE RESULTS before the next successful calculation. Use --keep-history to disable automatic cleanup. cleanup.json in the latest run records removals.
