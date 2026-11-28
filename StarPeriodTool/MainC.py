r"""# Star Period Tool - standalone research application

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
"""

# ANALYZE - complete embedded application module
ANALYZE_SOURCE = r'''"""Reproducible period comparison for a single numeric photometric series."""
import argparse
import hashlib
import json
import math
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import astropy
from uncertainties import difference_noise, propagate_vr, method_error_usage
from astropy.timeseries import LombScargle

ROOT = Path(__file__).resolve().parent
METHODS = ('ls', 'fourier', 'pdm', 'wwz')


def parser():
    p = argparse.ArgumentParser(description='Compare periods of one object / one photometric band. Period limits are in days.', epilog='Standalone switches: --discover (broad screen), --basic, --no-clip, --no-recommend, --step-by-step, --preprocess-only, --open-report, --manual, --self-test.')
    p.add_argument('--input', required=True)
    p.add_argument('--object-name', default='Unnamed object')
    p.add_argument('--output-dir', default=str(ROOT / 'results'))
    p.add_argument('--time-col')
    p.add_argument('--signal-col')
    p.add_argument('--error-col')
    p.add_argument('--noise-estimate', choices=['none','difference'], default='none', help='Explicit empirical common noise for perturbations when measurement errors are absent')
    for name in ('vr-v-col','vr-r-col','vr-v-error-col','vr-r-error-col'):
        p.add_argument('--'+name)
    p.add_argument('--vr-error-correlation', type=float, default=0.)
    p.add_argument('--band-col')
    p.add_argument('--band', help='Analyze only this band; bands are never merged automatically')
    p.add_argument('--time-unit', choices=['days', 'hours', 'minutes', 'seconds'], default='days')
    p.add_argument('--signal-kind', choices=['auto', 'magnitude', 'flux', 'vr', 'other'], default='auto')
    p.add_argument('--min-period', type=float, required=True, help='Shortest trial period in days; choose for the target class')
    p.add_argument('--max-period', type=float, required=True, help='Longest trial period in days')
    p.add_argument('--samples-per-peak', type=int, default=10)
    p.add_argument('--max-grid-size', type=int, default=200000)
    p.add_argument('--search-windows', help='JSON list of disjoint frequency intervals (cycles/day); gaps are not searched')
    p.add_argument('--search-origin', choices=['manual','known','discovery'], default='manual')
    p.add_argument('--scout-max-points', type=int, default=5000000)
    p.add_argument('--methods', nargs='+', choices=METHODS, default=list(METHODS))
    p.add_argument('--harmonics', type=int, default=2)
    p.add_argument('--auto-harmonics', action='store_true', help='Select advanced-model harmonics using nested blocked validation')
    p.add_argument('--max-harmonics', type=int, default=6)
    p.add_argument('--harmonic-folds', type=int, default=3)
    p.add_argument('--cv-gap-points', type=int, default=0)
    p.add_argument('--uncertainty-mode', choices=['iid', 'block'], default='iid')
    p.add_argument('--block-length', type=int, default=0, help='0 estimates a separate length in each observing segment')
    p.add_argument('--bins', type=int, default=10)
    p.add_argument('--wwz-centers', type=int, default=32)
    p.add_argument('--wwz-decay', type=float, default=0.0125)
    p.add_argument('--bootstrap', '--n-monte-carlo', type=int, default=0,
                   help='Full-grid measurement perturbations (requires errors); expensive with WWZ')
    p.add_argument('--advanced', action='store_true', help='Refine alternatives and fit a joint multi-period model')
    p.add_argument('--validation-input', help='Optional independent table for advanced-model prediction without refitting')
    p.add_argument('--max-modes', type=int, default=3)
    p.add_argument('--refine-candidates', type=int, default=3)
    p.add_argument('--bic-improvement', type=float, default=10.)
    p.add_argument('--uncertainty-trials', type=int, default=30)
    p.add_argument('--recommend', action='store_true', help='Run blocked validation and injection/recovery comparison')
    p.add_argument('--recommend-trials', type=int, default=12)
    p.add_argument('--cv-folds', type=int, default=5)
    p.add_argument('--recovery-tolerance', type=float, default=.01)
    p.add_argument('--clip-sigma', type=float, help='Optional one-pass clipping of residuals; e.g. 3')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--no-show-plots', action='store_true', help='Compatibility option: plots are always saved')
    return p


def normalized(s):
    return ''.join(c.lower() for c in str(s) if c.isalnum())


def select_column(df, explicit, aliases, required=True):
    if explicit:
        if explicit not in df.columns:
            raise ValueError(f'Column {explicit!r} not found. Available: {list(df.columns)}')
        return explicit
    matches = [c for c in df.columns if normalized(c) in aliases]
    if len(matches) > 1:
        raise ValueError(f'Ambiguous columns {matches}; specify the column explicitly.')
    if not matches and required:
        raise ValueError(f'Column not detected; specify explicitly. Available: {list(df.columns)}')
    return matches[0] if matches else None


def read_observation_table(path):
    path = Path(path)
    if path.suffix.lower() in ('.fits', '.fit', '.fts'):
        from astropy.table import Table
        df = Table.read(path).to_pandas()
    else:
        first = next((line.strip() for line in path.read_text(encoding='utf-8-sig').splitlines()
                      if line.strip() and not line.lstrip().startswith('#')), '')
        if not first: raise ValueError('Input table is empty.')
        sep = ',' if ',' in first else ('\t' if '\t' in first else r'\s+')
        import re
        tokens = first.split(sep) if sep != r'\s+' else re.split(r'\s+', first)
        def numeric(value):
            try: float(value.strip()); return True
            except ValueError: return False
        headerless = all(numeric(value) for value in tokens)
        if headerless and len(tokens) not in (2,3):
            raise ValueError('Headerless input requires 2 or 3 columns: time, signal, optional error. Add explicit headers otherwise.')
        df = pd.read_csv(path, sep=sep, engine='python', comment='#',
                         header=None if headerless else 0, encoding='utf-8-sig')
        if headerless: df.columns=['time','signal']+(['error'] if len(df.columns)==3 else [])
    if df.empty:
        raise ValueError('Input table is empty.')
    return df


def load_data(args):
    df = read_observation_table(args.input)
    input_rows = len(df)
    band_col = select_column(df, args.band_col, {'band', 'filter', 'passband'}, False)
    if args.band is not None and band_col is None:
        raise ValueError('--band requires a band column.')
    if band_col:
        if args.band is not None:
            df = df.loc[df[band_col].astype(str) == args.band].copy()
        elif df[band_col].nunique(dropna=False) > 1:
            raise ValueError('Multiple bands found. Select one using --band; do not mix zero points.')
    tc = select_column(df, args.time_col, {'jd', 'hjd', 'bjd', 'mjd', 'time'})
    yc = select_column(df, args.signal_col, {'mag', 'magnitude', 'flux', 'vmag', 'gmag', 'rmag', 'brightness', 'signal', 'y', 'vr'})
    ec = select_column(df, args.error_col, {normalized(yc) + 'err', normalized(yc) + 'error', normalized(yc) + 'sigma', 'e' + normalized(yc), 'dy', 'yerr', 'error', 'err', 'sigma'}, False)
    df,propagated=propagate_vr(df,args,yc)
    if propagated:
        if ec is not None: raise ValueError('Choose either a ratio error column or component-error propagation, not both.')
        ec=propagated['column']
    error_info=propagated or dict(source='supplied_column' if ec else 'unavailable',column=ec)
    if len({c for c in (tc, yc, ec) if c is not None}) != (3 if ec else 2):
        raise ValueError('Time, signal and error columns must be distinct.')
    cols = [tc, yc] + ([ec] if ec else [])
    data = df[cols].apply(pd.to_numeric, errors='coerce')
    good = np.isfinite(data).all(axis=1)
    if ec:
        good &= data[ec] > 0
    excluded = df.loc[~good].copy()
    data = data.loc[good].sort_values(tc, kind='stable')
    if len(data) < max(12, 2 * args.harmonics + 4):
        raise ValueError('Too few valid observations (need at least 12 and enough for the harmonic model).')
    factor = {'days': 1., 'hours': 24., 'minutes': 1440., 'seconds': 86400.}[args.time_unit]
    raw_t = data[tc].to_numpy(float)
    epoch = float(raw_t[0])
    t = (raw_t - epoch) / factor
    y = data[yc].to_numpy(float)
    dy = data[ec].to_numpy(float) if ec else None
    if np.ptp(t) <= 0 or len(np.unique(t)) < 8:
        raise ValueError('Need at least eight distinct times spanning a positive baseline.')
    if np.ptp(y) <= np.finfo(float).eps * max(1., np.max(np.abs(y))):
        raise ValueError('The signal is constant within floating-point precision.')
    label = str(yc)
    if 'Signal Label' in df:
        labels = df.loc[good, 'Signal Label'].dropna().astype(str).unique()
        if len(labels) == 1:
            label = labels[0]
    kind = args.signal_kind
    if kind == 'auto':
        kind = 'vr' if normalized(label) == 'vr' else 'magnitude' if 'mag' in normalized(label) else ('flux' if 'flux' in normalized(label) else 'other')
    if normalized(label) == 'vr' and kind in ('magnitude', 'flux'):
        raise ValueError('V/R-labelled data cannot be treated as magnitude or flux; use --signal-kind vr.')
    if kind == 'vr':
        label = 'V/R'
    notes = []
    if 'camera' in df.columns and df['camera'].nunique()>1:
        notes.append('Multiple cameras are present. Camera zero-point offsets and calibration differences are NOT automatically modeled; establish compatibility before interpretation.')
    if dy is None:
        notes.append('No measurement errors: equal fit weights. Perturbations require an explicit empirical noise model if no errors are supplied.')
    if kind == 'vr':
        notes.append('Spectroscopic V/R intensity ratio (dimensionless). Period candidates describe V/R variability, not established stellar pulsation periods. Spectral-line identification and intensity normalization require provenance.')
    if excluded.shape[0]:
        notes.append(f'Excluded {len(excluded)} rows with invalid numbers or non-positive errors; see excluded_rows.csv.')
    if len(np.unique(t)) != len(t):
        notes.append('Repeated timestamps retained as separate measurements; their independence must be checked.')
    if args.max_period > np.ptp(t) / 2:
        notes.append('Some trial periods cover fewer than two cycles; long-period candidates may represent trends.')
    meta = dict(input_rows=input_rows, selected_rows=len(df), valid_rows=len(t), time_column=tc,
                signal_column=yc, error_column=ec, label=label, signal_kind=kind, epoch_input_units=epoch,
                baseline_days=float(np.ptp(t)), median_cadence_days=float(np.median(np.diff(np.unique(t)))),
                max_gap_days=float(np.max(np.diff(np.unique(t)))), notes=notes, error_model=error_info)
    return t, y, dy, excluded, meta


def grid_segments(f):
    f=np.asarray(f)
    cuts=np.flatnonzero(np.diff(f)>3*np.median(np.diff(f)))+1 if len(f)>2 else []
    return np.split(np.arange(len(f)),cuts)


def grid_bounds(f,frequency):
    for ids in grid_segments(f):
        if f[ids[0]]-1e-12<=frequency<=f[ids[-1]]+1e-12:
            return float(f[ids[0]]),float(f[ids[-1]])
    return None


def grid_edge(f,frequency):
    bounds=grid_bounds(f,frequency)
    return bounds is None or min(abs(frequency-bounds[0]),abs(frequency-bounds[1]))<=2*np.median(np.diff(f))


def frequency_grid(t, args):
    advanced_h = args.max_harmonics if args.advanced and args.auto_harmonics else args.harmonics
    multiplier = max(advanced_h if ('fourier' in args.methods or args.advanced) else 1, args.bins if 'pdm' in args.methods else 1)
    if getattr(args,'search_windows',None):
        from discovery import merge_windows
        raw=json.loads(args.search_windows)
        if not isinstance(raw,list) or not raw:raise ValueError('search-windows must be a nonempty JSON list.')
        for pair in raw:
            if not isinstance(pair,list) or len(pair)!=2 or not all(isinstance(v,(int,float)) and np.isfinite(v) for v in pair) or not 0<pair[0]<pair[1]:
                raise ValueError('Each search window must have two finite positive ordered frequencies.')
            if pair[0]<1/args.max_period-1e-10 or pair[1]>1/args.min_period+1e-10:
                raise ValueError('Search windows must lie inside the declared period bounds.')
        windows=merge_windows(raw)
    else:windows=[[1/args.max_period,1/args.min_period]]
    sizes=[max(3,math.ceil((hi-lo)*np.ptp(t)*args.samples_per_peak*multiplier)+1) for lo,hi in windows]
    n=sum(sizes)
    if n>args.max_grid_size:
        raise ValueError(f'Need {n} trial frequencies (limit {args.max_grid_size}). Narrow the range or explicitly increase --max-grid-size. Grid will not be silently coarsened.')
    return np.concatenate([np.linspace(lo,hi,n) for (lo,hi),n in zip(windows,sizes)])


def pdm(t, y, f, bins):
    """Pooled within-bin variance / sample variance; two phase origins averaged.
    Singleton bins contribute zero degrees of freedom. Require >=80% usable data.
    """
    centered = y - np.mean(y)
    var = np.var(centered, ddof=1)
    out = np.full(len(f), np.nan)
    if var <= 0:
        return out
    for start in range(0, len(f), 256):
        freq = f[start:start + 256]
        values = []
        for shift in (0., .5):
            index = np.floor((t[None, :] * freq[:, None] * bins + shift) % bins).astype(int)
            numerator = np.zeros(len(freq)); dof = np.zeros(len(freq)); used = np.zeros(len(freq))
            for b in range(bins):
                mask = index == b
                count = mask.sum(axis=1)
                total = mask @ centered
                squares = mask @ (centered * centered)
                valid = count >= 2
                numerator[valid] += np.maximum(0, squares[valid] - total[valid] ** 2 / count[valid])
                dof[valid] += count[valid] - 1
                used[valid] += count[valid]
            valid = (dof > 0) & (used >= .8 * len(t))
            theta = np.full(len(freq), np.nan)
            theta[valid] = numerator[valid] / dof[valid] / var
            values.append(theta)
        out[start:start + len(freq)] = np.mean(values, axis=0)
    return out


def wwz(t, y, f, centers, decay):
    """Foster WWZ using temporal weights only; no interpolation across gaps."""
    matrix = np.full((len(f), len(centers)), np.nan)
    centered = y - np.mean(y)
    for i, freq in enumerate(f):
        x = 2 * np.pi * freq * (t[None, :] - centers[:, None])
        w = np.exp(-decay * x*x)
        sw = w.sum(axis=1)
        eff = sw*sw / np.maximum((w*w).sum(axis=1), np.finfo(float).tiny)
        for j in np.flatnonzero(eff >= 8):
            # Avoid displaying a local estimate centered in an unobserved gap.
            radius = 1 / (2 * np.pi * freq * np.sqrt(decay))
            if np.min(np.abs(t - centers[j])) > radius:
                continue
            a = np.column_stack((np.ones(len(t)), np.cos(x[j]), np.sin(x[j])))
            aw = a * np.sqrt(w[j, :, None])
            coef, _, rank, singular = np.linalg.lstsq(aw, centered * np.sqrt(w[j]), rcond=None)
            if rank < 3 or singular[-1] / singular[0] < 1e-8:
                continue
            mean = np.sum(w[j] * centered) / sw[j]
            total = np.sum(w[j] * (centered - mean)**2)
            residual = np.sum(w[j] * (centered - a @ coef)**2)
            if total > 0:
                matrix[i, j] = (eff[j] - 3) * max(total - residual, 0) / (2 * max(residual, total * 1e-14))
    count = np.isfinite(matrix).sum(axis=1)
    spectrum = np.full(len(f), np.nan)
    valid = count >= max(3, math.ceil(len(centers) * .2))
    spectrum[valid] = np.nansum(matrix[valid], axis=1) / count[valid]
    return spectrum, matrix


def evaluate(method, t, y, dy, f, args, centers):
    if method == 'pdm':
        return pdm(t, y, f, args.bins), None
    if method == 'wwz':
        return wwz(t, y, f, centers, args.wwz_decay)
    terms = args.harmonics if method == 'fourier' else 1
    model = LombScargle(t, y, dy, nterms=terms, fit_mean=True, center_data=True)
    try:
        power = model.power(f, method='chi2')
    except np.linalg.LinAlgError:
        # Exact cadence harmonics can have rank-deficient designs. Retain the
        # rest of the search instead of terminating the complete analysis.
        power = np.full(len(f), np.nan)
        for i, frequency in enumerate(f):
            try:
                power[i] = model.power(frequency, method='chi2')
            except np.linalg.LinAlgError:
                pass
    return power, None


def peak_indices(score, f, baseline, lower=False, count=5):
    z = -score if lower else score
    z = np.where(np.isfinite(z), z, -np.inf)
    left=np.r_[-np.inf,z[:-1]];right=np.r_[z[1:],-np.inf]
    for ids in grid_segments(f):left[ids[0]]=-np.inf;right[ids[-1]]=-np.inf
    candidates=np.flatnonzero((z>=left)&(z>=right)&np.isfinite(z))
    kept = []
    for i in candidates[np.argsort(z[candidates])[::-1]]:
        if all(abs(f[i] - f[j]) >= 1 / baseline for j in kept):
            kept.append(int(i))
            if len(kept) == count:
                break
    return kept


def run(args, preprocessing_callback=None):
    if not (np.isfinite(args.min_period) and np.isfinite(args.max_period) and 0 < args.min_period < args.max_period):
        raise ValueError('Require 0 < min-period < max-period, both finite.')
    if args.samples_per_peak < 2 or args.harmonics < 1 or args.bins < 2 or args.wwz_centers < 3 or not np.isfinite(args.wwz_decay) or args.wwz_decay <= 0 or args.bootstrap < 0:
        raise ValueError('Invalid grid, harmonic, bin, WWZ or bootstrap settings.')
    if args.recommend_trials < 1 or args.cv_folds < 3 or not (0 < args.recovery_tolerance < .5):
        raise ValueError('Invalid recommendation trials, folds or relative tolerance.')
    if args.clip_sigma is not None and (not np.isfinite(args.clip_sigma) or args.clip_sigma <= 0):
        raise ValueError('clip-sigma must be positive and finite.')
    if args.validation_input and not args.advanced:
        raise ValueError('--validation-input requires --advanced.')
    if args.max_harmonics < 1 or args.harmonic_folds < 2 or args.cv_gap_points < 0 or args.block_length < 0:
        raise ValueError('Invalid harmonic selection or block resampling settings')
    if args.auto_harmonics and not args.advanced:
        raise ValueError('--auto-harmonics requires --advanced')
    if args.max_modes < 1 or args.refine_candidates < 1 or not np.isfinite(args.bic_improvement) or args.bic_improvement <= 0 or args.uncertainty_trials < 0:
        raise ValueError('Invalid advanced-model settings.')
    args.methods = list(dict.fromkeys(args.methods))
    t, y, dy, excluded, meta = load_data(args)
    estimated_sigma=None
    if dy is None and args.noise_estimate=='difference':
        estimated_sigma,meta['noise_estimate']=difference_noise(t,y)
        meta['notes'].append('Estimated difference-MAD noise is used for simulations only; fit weights remain equal. This is not an instrumental error.')
    elif args.noise_estimate=='difference':
        meta['notes'].append('Noise estimate not used: supplied or propagated errors take priority.')
    if args.bootstrap and dy is None and estimated_sigma is None:
        raise ValueError('Measurement perturbations require a valid error column, V/R propagation or explicit --noise-estimate difference.')
    meta['method_error_usage']=method_error_usage(args.methods,dy is not None,args.bootstrap>0)
    meta['perturbation_noise_source']=meta['error_model']['source'] if dy is not None else ('estimated_difference_mad' if estimated_sigma is not None else 'unavailable')
    f = frequency_grid(t, args)
    meta['searched_frequency_windows']=[[float(f[ids[0]]),float(f[ids[-1]])] for ids in grid_segments(f)]
    meta['search_origin']=args.search_origin
    if args.search_origin=='discovery':meta['notes'].append('Data-selected windows: method comparisons, simulations and internal validation are conditional on this prior selection. Gaps between windows are not searched.')
    # Every run gets its own directory; previous results are never deleted.
    out = Path(args.output_dir) / datetime.now(timezone.utc).strftime('run_%Y%m%dT%H%M%S_%fZ')
    out.mkdir(parents=True, exist_ok=False)
    print(f'Output: {out}\nRows: {len(t)}; frequency points: {len(f)}', flush=True)
    raw_t, raw_y, raw_dy = t.copy(), y.copy(), None if dy is None else dy.copy()
    original_periods = None
    if args.clip_sigma is not None:
        from recommendation import initial_periods, residual_clip
        print('Preliminary search for residual clipping...', flush=True)
        original_periods = initial_periods(t,y,dy,f,args)
        keep, clip_note = residual_clip(t,y,dy,original_periods,args)
        pd.DataFrame({'time_days_from_epoch':t,'signal':y,'error':dy if dy is not None else np.nan,'retained':keep}).to_csv(out/'clipping_audit.csv',index=False)
        meta['notes'].append(clip_note)
        meta['pre_clip_rows'] = len(t)
        t,y,dy = t[keep],y[keep],None if dy is None else dy[keep]
        meta['valid_rows'] = len(t)
        meta['baseline_days'] = float(np.ptp(t))
        meta['median_cadence_days'] = float(np.median(np.diff(np.unique(t))))
        meta['max_gap_days'] = float(np.max(np.diff(np.unique(t))))
    excluded.to_csv(out / 'excluded_rows.csv', index=False)
    pd.DataFrame({'time_days_from_epoch': t, 'signal': y, 'error': dy if dy is not None else np.nan}).to_csv(out / 'used_data.csv', index=False)
    pd.DataFrame({'time_days_from_epoch':t,'measurement_error':dy if dy is not None else np.nan,'estimated_common_noise':estimated_sigma if estimated_sigma is not None else np.nan}).to_csv(out/'error_audit.csv',index=False)
    if preprocessing_callback is not None:
        preview = dict(parameters=vars(args), data=meta,
                       input_sha256=hashlib.sha256(Path(args.input).read_bytes()).hexdigest())
        if not preprocessing_callback(out, preview):
            (out/'PREPROCESSING_ONLY.json').write_text(json.dumps(preview, indent=2), encoding='utf-8')
            return out
    print(f'Detailed grid: {len(f):,} frequencies; base methods: {len(args.methods)}; Monte Carlo repeats per method: {args.bootstrap}. Additional validation may require many more searches.',flush=True)
    perturbation_scale=dy if dy is not None else estimated_sigma
    centers = np.linspace(t.min(), t.max(), args.wwz_centers)
    rng = np.random.default_rng(args.seed)
    perturbations = rng.normal(size=(args.bootstrap, len(y))) if args.bootstrap else []
    rows, peaks, spectra, samples = [], [], {}, []
    for method in args.methods:
        print(f'Computing {method}...', flush=True)
        started = time.perf_counter()
        score, matrix = evaluate(method, t, y, dy, f, args, centers)
        elapsed = time.perf_counter() - started
        score = np.where(np.isfinite(score), score, np.nan)
        if method in ('ls', 'fourier'):
            # Ill-conditioned fits can generate nonphysical powers.
            score = np.where((score >= -1e-8) & (score <= 1 + 1e-8), np.clip(score, 0, 1), np.nan)
        spectra[method] = score
        best = peak_indices(score, f, np.ptp(t), method == 'pdm')
        if not best:
            rows.append(dict(method=method, status='insufficient_support', runtime_seconds=elapsed,monte_carlo_status='not_run_no_supported_baseline_peak' if args.bootstrap else 'disabled'))
            continue
        idx = best[0]; period = float(1 / f[idx])
        row = dict(method=method, status='candidate', period_days=period, score=float(score[idx]),
                   statistic='theta' if method == 'pdm' else ('WWZ' if method == 'wwz' else 'normalized_chi2_reduction'),
                   cycles=float(np.ptp(t) / period), phase_coverage=float(len(np.unique((t / period % 1 * args.bins).astype(int))) / args.bins),
                   grid_period_step_days=float((f[1] - f[0]) / f[idx]**2),
                   near_boundary=bool(grid_edge(f,f[idx])), runtime_seconds=elapsed)
        if method == 'ls':
            if args.search_origin!='discovery':
                fap=float(LombScargle(t, y, dy).false_alarm_probability(score[idx], method='baluev', minimum_frequency=f[0], maximum_frequency=f[-1]))
                row['fap_baluev']=fap if np.isfinite(fap) else None
            else:row['fap_note']='Not reported: search windows were selected using the same observations.'
        for rank, j in enumerate(best, 1):
            peaks.append(dict(method=method, rank=rank, period_days=float(1 / f[j]), frequency_per_day=float(f[j]), score=float(score[j])))
        draws = []
        row['monte_carlo_status']='enabled' if args.bootstrap else 'disabled'
        row['monte_carlo_trials']=args.bootstrap
        for k, noise in enumerate(perturbations):
            if k%max(1,args.bootstrap//10)==0:print(f'Monte Carlo {method}: {k+1}/{args.bootstrap}',flush=True)
            sim_score, _ = evaluate(method, t, y + perturbation_scale * noise, dy, f, args, centers)
            if method in ('ls','fourier'):sim_score=np.where((sim_score>=-1e-8)&(sim_score<=1+1e-8),sim_score,np.nan)
            candidates = peak_indices(sim_score, f, np.ptp(t), method == 'pdm', 1)
            value = float(1 / f[candidates[0]]) if candidates else np.nan
            draws.append(value)
            samples.append(dict(method=method, iteration=k, period_days=value))
        if draws:
            valid = np.asarray(draws)[np.isfinite(draws)]
            row['perturbation_successes'] = len(valid)
            if len(valid):
                row.update(zip(('perturbation_p16_days', 'perturbation_median_days', 'perturbation_p84_days'), map(float, np.percentile(valid, [16, 50, 84]))))
                in_peak=np.abs(1/valid-f[idx])<=1/np.ptp(t)
                row['same_peak_fraction']=float(in_peak.sum()/args.bootstrap)
                row['same_peak_fraction_among_successes']=float(in_peak.mean())
                if in_peak.any():
                    row['conditional_peak_p16_days'],row['conditional_peak_p84_days']=map(float,np.percentile(valid[in_peak],[16,84]))
            row['monte_carlo_failures']=args.bootstrap-len(valid)
        rows.append(row)
        if matrix is not None:
            np.savez_compressed(out / 'wwz_map.npz', frequency_per_day=f, time_days_from_epoch=centers, wwz=matrix)
            fig, ax = plt.subplots(figsize=(10, 5))
            im = ax.pcolormesh(centers, 1/f[::-1], matrix[::-1], shading='auto', rasterized=True)
            ax.set(xlabel='Time from epoch (days)', ylabel='Period (days)', title='WWZ: blank cells have insufficient local support')
            fig.colorbar(im, ax=ax, label='WWZ'); fig.tight_layout(); fig.savefig(out / 'wwz_map.png', dpi=160); plt.close(fig)
    periods = [row['period_days'] for row in rows if 'period_days' in row]
    if len(periods) > 1 and max(periods) / min(periods) > 1.05:
        meta['notes'].append('Methods disagree by more than 5 percent. Inspect aliases, harmonics and sampling; no unique adopted period is established.')
    if args.bootstrap and args.bootstrap < 100:
        meta['notes'].append('Fewer than 100 perturbations: use this run only as a smoke test of the uncertainty workflow.')
    pd.DataFrame(rows).to_csv(out / 'comparison.csv', index=False)
    pd.DataFrame(peaks,columns=['method','rank','period_days','frequency_per_day','score']).to_csv(out / 'top_candidates.csv', index=False)
    pd.DataFrame(samples, columns=['method', 'iteration', 'period_days']).to_csv(out / 'perturbation_periods.csv', index=False)
    window = np.empty(len(f))
    for start in range(0, len(f), 256):
        window[start:start+256] = np.abs(np.exp(2j*np.pi*f[start:start+256, None]*t).mean(axis=1))**2
    pd.DataFrame({'frequency_per_day': f, 'period_days': 1/f, 'spectral_window': window, **spectra}).to_csv(out / 'periodograms.csv', index=False)
    plot_results(out, t, y, dy, f, window, spectra, rows, meta, args)
    payload = dict(schema_version=1, parameters=vars(args), input_sha256=hashlib.sha256(Path(args.input).read_bytes()).hexdigest(),
                   data=meta, results=rows, versions=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, astropy=astropy.__version__, matplotlib=matplotlib.__version__))
    if original_periods is not None:
        pd.DataFrame([dict(method=row['method'],before_period_days=original_periods.get(row['method']),after_period_days=row.get('period_days')) for row in rows]).to_csv(out/'clipping_comparison.csv',index=False)
    if args.recommend:
        from recommendation import recommend
        payload['recommendation'] = recommend(raw_t,raw_y,raw_dy,f,args,out,original_periods,meta['error_model'])
    if args.advanced:
        from advanced import advanced
        payload['advanced'] = advanced(raw_t,raw_y,raw_dy,f,args,out,meta)
    (out / 'run.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    write_report(out, payload)
    if args.recommend:
        with (out/'report.md').open('a',encoding='utf-8') as report:
            report.write('\n\n## Automatic recommendation\n\nSee [validation results](recommendation.md). Evaluation uses data before optional clipping.\n')
    if args.advanced:
        with (out/'report.md').open('a',encoding='utf-8') as report:
            report.write('\n\n## Refinement and multiple periods\n\nSee [joint model and validation](advanced.md).\n')
    print(pd.DataFrame(rows).to_string(index=False), flush=True)
    return out


def plot_results(out, t, y, dy, f, window, spectra, rows, meta, args):
    from presentation import plot_method_results
    plot_method_results(out,t,y,dy,f,window,spectra,rows,meta,args)
    fig, axes = plt.subplots(len(spectra)+1, 1, figsize=(10, 3*(len(spectra)+1)), squeeze=False)
    for ax, (name, values) in zip(axes[:, 0], spectra.items()):
        for ids in grid_segments(f):ax.plot(1/f[ids],values[ids],lw=.8,color='tab:blue')
        ax.set(xscale='log',ylabel=name,xlabel='Period (days)')
    for ids in grid_segments(f):axes[-1,0].plot(1/f[ids],window[ids],lw=.8,color='gray')
    axes[-1, 0].set(xscale='log', ylabel='Spectral window', xlabel='Period (days)')
    for ax in axes[:, 0]: ax.set_xlim(args.min_period, args.max_period)
    fig.suptitle(args.object_name); fig.tight_layout(); fig.savefig(out / 'periodograms.png', dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4)); ax.errorbar(t, y, yerr=dy, fmt='.', ms=4)
    ax.set(xlabel='Time from epoch (days)', ylabel=meta['label'], title=args.object_name)
    if meta['signal_kind'] == 'magnitude': ax.invert_yaxis()
    fig.tight_layout(); fig.savefig(out / 'light_curve.png', dpi=160); plt.close(fig)
    successful = [r for r in rows if 'period_days' in r]
    if not successful: return
    fig, axes = plt.subplots(len(successful), 1, figsize=(9, 3*len(successful)), squeeze=False)
    for ax, row in zip(axes[:, 0], successful):
        phase = (t / row['period_days']) % 1
        ax.errorbar(phase, y, yerr=dy, fmt='.', ms=4)
        ax.errorbar(phase+1, y, yerr=dy, fmt='.', ms=4, alpha=.4)
        ax.set(xlabel='Phase', ylabel=meta['label'], title=f"{row['method']}: P={row['period_days']:.8g} days")
        if meta['signal_kind'] == 'magnitude': ax.invert_yaxis()
    fig.tight_layout(); fig.savefig(out / 'phase_curves.png', dpi=160); plt.close(fig)


def write_report(out, payload):
    data = payload['data']; args = payload['parameters']
    lines = ['# Comparative analysis of methods for determining variable-star periodicity from photometric data',
             '', f"Object: {args['object_name']}", f"Source: {args['input']}",
             f"Observations: {data['valid_rows']}; baseline: {data['baseline_days']:.8g} days.",
             f"Envelope: {args['min_period']}–{args['max_period']} days. All methods use the same selected frequency grid; gaps between search windows are not tested.", '',
             '| Method | Period, days | Statistic | Cycles | Status |', '|---|---:|---:|---:|---|']
    if data['signal_kind'] == 'vr':
        lines[0] = '# Periodicity of the spectroscopic V/R indicator'
        lines.insert(2, 'Supplementary spectroscopic analysis. The signal is a dimensionless V/R intensity ratio, not a photometric magnitude. Candidate periods describe V/R variation; a pulsation origin has not been established.')
    for row in payload['results']:
        if 'period_days' in row:
            lines.append(f"| {row['method']} | {row['period_days']:.9g} | {row['score']:.6g} | {row['cycles']:.3g} | {'search boundary' if row['near_boundary'] else 'candidate'} |")
        else:
            lines.append(f"| {row['method']} | - | - | - | insufficient data |")
    lines += ['', '## Interpretation',
              'Results are candidates, not automatically confirmed pulsation periods. Inspect P/2 and 2P harmonics, alternative peaks and the spectral window. The program does not select a winner by voting among methods.',
              'LS is a weighted sinusoid with a floating mean. Fourier is multiharmonic regression (generalized LS); these are related models, not independent confirmations. PDM is unweighted phase dispersion, with lower values preferred. WWZ provides time localization without photometric-error weights; its global statistic averages supported centers.',
              'Statistics from different methods cannot be compared directly. Baluev FAP for LS assumes independent Gaussian noise and applies to the specified search range; it is not the probability that the selected period is true.',
              'Grid spacing is not a period error. Perturbation percentiles describe sensitivity to assumed measurement errors with a full-range search, not calibrated confidence intervals. For multiple peaks inspect the distribution and same_peak_fraction. Zero scatter may indicate an overly coarse grid.',
              'No outlier or trend removal by default; optional clipping is recorded in clipping_audit.csv and may alter a pulsation signal. Each run analyzes one object and one band. For multiperiodic objects, several peaks do not replace a joint model and residual checks.', '', '## Data notes']
    lines += ['- ' + note for note in data['notes']]
    lines += ['', '## Measurement errors and noise estimates',
              'Measurement-error source: '+data.get('error_model',{}).get('source','unavailable'),
              'Perturbation-noise source: '+data.get('perturbation_noise_source','unavailable'),
              'Measured/propagated errors, approximate noise estimates and period uncertainties are different quantities. See error_audit.csv and run.json.',
              '| Method | Search weights | Error/noise perturbations |','|---|---|---|']
    for name,usage in data.get('method_error_usage',{}).items():
        lines.append(f"| {name} | {usage['fit_weights']} | {usage['error_perturbations']} |")
    if 'noise_estimate' in data:
        lines.append('Approximate common noise level: '+str(data['noise_estimate']['sigma'])+' in signal units. This adjacent-difference heuristic is affected by intrinsic variability and correlation.')
    if data.get('error_model',{}).get('source')=='propagated_vr':
        lines.append('V/R error uses first-order propagation with V-R error correlation rho='+str(data['error_model']['correlation'])+'. Rows with component relative error >20%: '+str(data['error_model']['high_relative_component_error_rows']))
    lines += ['', '## Reproducibility', 'Parameters, input SHA-256 and library versions: run.json. Numerical results: comparison.csv, periodograms.csv, top_candidates.csv. Excluded rows: excluded_rows.csv.',
              '', '## Methodological references',
              '- https://docs.astropy.org/en/stable/timeseries/lombscargle.html',
              '- Stellingwerf (1978), https://doi.org/10.1086/156444',
              '- Foster (1996), https://doi.org/10.1086/118137']
    (out / 'report.md').write_text('\n\n'.join(lines[:1]) + '\n' + '\n'.join(lines[1:]), encoding='utf-8')


def main(argv=None):
    p = parser(); args = p.parse_args(argv)
    try:
        run(args)
    except (ValueError, OSError, np.linalg.LinAlgError) as exc:
        p.exit(2, f'Analysis error: {exc}\n')


if __name__ == '__main__':
    main()
'''

# RECOMMENDATION - complete embedded application module
RECOMMENDATION_SOURCE = r'''"""Auditable, conditional method recommendation; no universal-best claim."""
import math
import numpy as np
import pandas as pd


def fit_predict(t, y, dy, period, target, harmonics=2):
    def design(times):
        phase = 2 * np.pi * times / period
        return np.column_stack([np.ones(len(times))] + [v for k in range(1, harmonics+1) for v in (np.sin(k*phase), np.cos(k*phase))])
    x = design(t)
    weights = np.ones(len(t)) if dy is None else 1 / dy
    coef, _, rank, singular = np.linalg.lstsq(x * weights[:, None], y * weights, rcond=None)
    if rank < x.shape[1] or singular[-1] / singular[0] < 1e-10:
        raise ValueError('Insufficient independent phases for prediction')
    return design(target) @ coef


def search(method, t, y, dy, frequencies, args):
    from analyze import evaluate, peak_indices
    score, _ = evaluate(method, t, y, dy, frequencies, args, np.linspace(t.min(), t.max(), args.wwz_centers))
    if method in ('ls', 'fourier'):
        score = np.where((score >= -1e-8) & (score <= 1+1e-8), score, np.nan)
    peaks = peak_indices(score, frequencies, np.ptp(t), method == 'pdm', 1)
    return float(1 / frequencies[peaks[0]]) if peaks else None


def initial_periods(t, y, dy, frequencies, args):
    return {method: search(method,t,y,dy,frequencies,args) for method in args.methods}


def residual_clip(t, y, dy, periods, args):
    """One conservative pass: only reject points flagged by EVERY candidate model.
    Uses MAD plus supplied errors; never estimates errors from a trimmed series.
    """
    threshold = args.clip_sigma
    keep = np.ones(len(t), dtype=bool)
    masks = []
    for period in periods.values():
        if period is None: continue
        try:
            prediction = fit_predict(t,y,dy,period,t,args.harmonics)
        except ValueError:
            continue
        residual = y-prediction
        center = np.median(residual)
        mad = 1.4826*np.median(np.abs(residual-center))
        floor = np.finfo(float).eps*max(1.,np.max(np.abs(y)))
        scale = np.maximum(mad, dy) if dy is not None else np.full(len(y),mad)
        masks.append(np.abs(residual-center) > threshold*np.maximum(scale,floor))
    if not masks:
        return keep, 'No supported preliminary model; clipping skipped.'
    rejected = np.logical_and.reduce(masks)
    if rejected.sum() > .1*len(t) or (~rejected).sum() < max(12,2*args.harmonics+4) or len(np.unique(t[~rejected])) < 8:
        return keep, 'Clipping would remove too much data or leave insufficient support; skipped.'
    return ~rejected, f'One residual-clipping pass at {threshold:g} sigma; all {len(masks)} supported candidate models must flag a point.'


def wilson(successes, count):
    if not count: return (0.,1.)
    z=1.95996398454; p=successes/count
    center=(p+z*z/(2*count))/(1+z*z/count)
    half=z*math.sqrt(p*(1-p)/count+z*z/(4*count*count))/(1+z*z/count)
    return center-half,center+half


def choose(metrics, trials):
    """Declared gates, followed by paired prediction comparison (not a p-value)."""
    eligible=[]
    for row in metrics:
        reasons=[]
        if trials < 12: reasons.append('fewer_than_12_injections')
        if row['cv_success_fraction'] < 1: reasons.append('incomplete_cross_validation')
        if row['stable_fold_fraction'] < .8: reasons.append('unstable_period')
        if row['cv_mean_gain'] is None or row['cv_mean_gain'] <= .1: reasons.append('weak_out_of_sample_prediction')
        if row['recovery_wilson_low'] < .5: reasons.append('weak_injection_recovery')
        if row['cycles'] < 2: reasons.append('fewer_than_two_cycles')
        if row['near_boundary']: reasons.append('search_boundary')
        row['ineligible_reasons']=reasons
        if not reasons: eligible.append(row)
    if not eligible:
        return dict(status='inconclusive',method=None,period_days=None,comparable_methods=[],reason='No method passed all declared validation gates.')
    eligible.sort(key=lambda r:r['cv_mean_gain'],reverse=True)
    leader=eligible[0]; comparable=[leader['method']]
    for row in eligible[1:]:
        difference=np.array(leader['fold_gains'])-np.array(row['fold_gains'])
        # Correlated folds: descriptive one-SE equivalence rule, not a confidence test.
        se=float(np.std(difference,ddof=1)/np.sqrt(len(difference)))
        if float(np.mean(difference)) <= max(se,.02): comparable.append(row['method'])
    if len(comparable)>1:
        return dict(status='comparable',method=None,period_days=None,comparable_methods=comparable,reason='Prediction differences do not exceed the declared one-SE / 0.02-gain margin; no unique best method.')
    return dict(status='conditional_recommendation',method=leader['method'],period_days=leader['period_days'],comparable_methods=comparable,reason='Passed recovery, stability and prediction gates; highest distinguishable validation gain among eligible methods.')


def recommend(t,y,dy,frequencies,args,out,periods=None,error_info=None):
    periods=periods or initial_periods(t,y,dy,frequencies,args)
    rng=np.random.default_rng(args.seed+7103)
    # Contiguous time blocks. Frequency search and coefficient fitting both use
    # training observations only; all methods receive identical folds.
    folds=np.array_split(np.arange(len(t)),args.cv_folds)
    cv=[]; injection=[]; metrics=[]
    sigma=(1.4826*np.median(np.abs(np.diff(y)-np.median(np.diff(y))))/np.sqrt(2)) if dy is None else None
    if sigma is not None: sigma=max(float(sigma),np.std(y)*.05,np.finfo(float).eps)
    noise_info=None
    if dy is None and args.noise_estimate=='difference':
        from uncertainties import difference_noise
        sigma,noise_info=difference_noise(t,y)
    noise=np.full(len(y),sigma) if dy is None else dy
    amplitude=max(float((np.percentile(y,95)-np.percentile(y,5))/2),float(np.median(noise)))
    scenarios=[]
    for i in range(args.recommend_trials):
        # Log-stratified periods span the REQUESTED range independently of winners.
        frac=(i+rng.uniform(.1,.9))/args.recommend_trials
        from analyze import grid_segments
        windows=[(1/frequencies[ids[-1]],1/frequencies[ids[0]]) for ids in grid_segments(frequencies)]
        lengths=np.array([np.log(hi/lo) for lo,hi in windows]);coordinate=frac*lengths.sum()
        wi=min(int(np.searchsorted(np.cumsum(lengths),coordinate)),len(windows)-1)
        offset=coordinate-(np.sum(lengths[:wi]) if wi else 0.)
        period=windows[wi][0]*np.exp(offset)
        phase=2*np.pi*t/period+rng.uniform(0,2*np.pi)
        shape=i%3
        signal=np.sin(phase)
        if shape==1: signal += .5*np.sin(2*phase+.4)
        if shape==2: signal += .3*np.sin(2*phase+.7)+.2*np.sin(3*phase+.2)
        signal=signal/np.sqrt(np.mean(signal**2)) * amplitude/np.sqrt(2)
        scenarios.append((period,shape,np.median(y)+signal+rng.normal(size=len(y))*noise))
    for method in args.methods:
        print(f'Validating {method}: {args.cv_folds} folds + {args.recommend_trials} injected signals...',flush=True)
        full=periods.get(method); gains=[]; stable=0; success=0
        for fold,test in enumerate(folds):
            train=np.setdiff1d(np.arange(len(t)),test)
            period=None; gain=None
            if len(train)>=max(12,2*args.harmonics+4) and len(np.unique(t[train]))>=8:
                period=search(method,t[train],y[train],None if dy is None else dy[train],frequencies,args)
                if period is not None:
                    try:
                        pred=fit_predict(t[train],y[train],None if dy is None else dy[train],period,t[test],args.harmonics)
                        train_weights=None if dy is None else 1/dy[train]**2
                        baseline=np.average(y[train],weights=train_weights)
                        weights=np.ones(len(test)) if dy is None else 1/dy[test]**2
                        denom=np.sum(weights*(y[test]-baseline)**2)
                        if denom>0:
                            gain=float(1-np.sum(weights*(y[test]-pred)**2)/denom)
                    except ValueError: pass
            if gain is not None and np.isfinite(gain):
                gains.append(gain); success+=1
                if full is not None and abs(period/full-1)<=args.recovery_tolerance: stable+=1
            else: gain=None
            cv.append(dict(method=method,fold=fold,train_points=len(train),test_points=len(test),period_days=period,prediction_gain=gain))
        recovered=0
        for i,(truth,shape,sim) in enumerate(scenarios):
            period=search(method,t,sim,dy,frequencies,args)
            error=abs(period/truth-1) if period is not None else None
            hit=bool(error is not None and error<=args.recovery_tolerance)
            recovered+=hit
            injection.append(dict(method=method,trial=i,shape=shape,true_period_days=truth,recovered_period_days=period,relative_error=error,success=hit,amplitude=amplitude))
        low,high=wilson(recovered,args.recommend_trials)
        metrics.append(dict(method=method,period_days=full,cycles=float(np.ptp(t)/full) if full else 0.,
                            near_boundary=bool(full is None or __import__('analyze').grid_edge(frequencies,1/full)),
                            cv_mean_gain=float(np.mean(gains)) if gains else None,fold_gains=gains,
                            cv_success_fraction=success/args.cv_folds,stable_fold_fraction=stable/args.cv_folds,
                            recovery_fraction=recovered/args.recommend_trials,recovery_wilson_low=low,recovery_wilson_high=high))
    decision=choose(metrics,args.recommend_trials)
    if getattr(args,'search_origin','manual')=='discovery':
        decision=dict(status='conditional_window_comparison',method=None,period_days=None,comparable_methods=[],reason='Windows were selected on the same full dataset. A unique validated winner is not claimed; metrics are exploratory and conditional.')
    pd.DataFrame(cv).to_csv(out/'recommendation_cv.csv',index=False)
    pd.DataFrame(injection).to_csv(out/'recommendation_injections.csv',index=False)
    pd.DataFrame([{k:v for k,v in row.items() if k!='fold_gains'} for row in metrics]).to_csv(out/'recommendation_metrics.csv',index=False)
    result=dict(scope='original_valid_data_before_optional_clipping',decision=decision,metrics=metrics,
                noise_model='supplied_independent_gaussian_errors' if dy is not None else 'heuristic_difference_MAD_gaussian_noise',estimated_noise=sigma,
                measurement_error_model=error_info,noise_estimate_details=noise_info,amplitude=amplitude,relative_period_tolerance=args.recovery_tolerance,
                limitations=['Conditional on chosen range, injected profiles, amplitude and noise model; not a universal ranking.',
                             'All candidate periods use the same harmonic predictor; validation compares period-search pipelines with this predictor.',
                             'Contiguous folds are dependent; the one-SE rule is descriptive, not a significance test.',
                             'Wilson intervals are descriptive for this stratified simulation design, not population confidence guarantees.',
                             'No red-noise model, multi-mode decomposition or proof that variability is pulsation.'])
    import json
    (out/'recommendation.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    lines=['# Method recommendation', '', 'Evaluation uses the original valid data BEFORE optional clipping.',
           f"Status: {decision['status']}",f"Recommended method: {decision['method'] or 'no unique method selected'}",
           f"Comparable methods: {', '.join(decision['comparable_methods']) or 'no'}",'',
           '| Method | Recovery fraction | Mean prediction gain | Stability across blocks |', '|---|---:|---:|---:|']
    for r in metrics: lines.append(f"| {r['method']} | {r['recovery_fraction']:.3f} | {r['cv_mean_gain']} | {r['stable_fold_fraction']:.3f} |")
    lines+=['','Thresholds and limitations: README.md; detailed rejection reasons and metrics: recommendation.json.',
            'conditional_recommendation means a conditional recommendation for this experiment; comparable means multiple comparable methods; inconclusive means insufficient data or stability.']
    lines += ['',decision['reason']]
    (out/'recommendation.md').write_text('\n'.join(lines),encoding='utf-8')
    return result
'''

# ADVANCED - complete embedded application module
ADVANCED_SOURCE = r'''"""Joint harmonic candidate models, local refinement and global re-search simulations."""
import json
import copy
from robustness import blocked_splits, select_harmonics, residual_blocks, draw_blocks
import numpy as np
import pandas as pd
from scipy.optimize import least_squares, linear_sum_assignment
from astropy.timeseries import LombScargle


def design(t, frequencies, harmonics):
    columns=[np.ones(len(t))]
    for f in frequencies:
        for k in range(1,harmonics+1):
            columns.extend([np.sin(2*np.pi*k*f*t),np.cos(2*np.pi*k*f*t)])
    return np.column_stack(columns)


def linear_fit(t,y,dy,frequencies,harmonics):
    x=design(t,frequencies,harmonics)
    w=np.ones(len(t)) if dy is None else 1/dy
    # Center the signal to avoid subtracting large photometric offsets.
    offset=float(np.mean(y))
    coef,_,rank,singular=np.linalg.lstsq(x*w[:,None],(y-offset)*w,rcond=None)
    if rank<x.shape[1] or singular[-1]/singular[0]<1e-9:
        raise ValueError('Rank-deficient joint model')
    coef[0]+=offset
    residual=y-x@coef
    sse=float(np.sum((residual*w)**2))
    parameters=x.shape[1]+len(frequencies)+(1 if dy is None else 0)
    if len(t)<=parameters+2: raise ValueError('Insufficient observations for joint model')
    deviance=sse if dy is not None else len(t)*np.log(max(sse/len(t),np.finfo(float).tiny))
    return dict(frequencies=list(map(float,frequencies)),coefficients=coef.tolist(),sse=sse,
                bic=float(deviance+parameters*np.log(len(t))),parameters=parameters)


def refine(t,y,dy,starts,grid,harmonics):
    if not len(starts): return linear_fit(t,y,dy,[],harmonics)
    starts=np.array(starts,float)
    radius=.5/np.ptp(t)
    from analyze import grid_bounds
    bounds=[grid_bounds(grid,f) for f in starts]
    if any(b is None for b in bounds):raise ValueError('Refinement seed lies outside selected windows')
    lo=np.maximum([b[0] for b in bounds],starts-radius);hi=np.minimum([b[1] for b in bounds],starts+radius)
    def residual(f):
        try:
            model=linear_fit(t,y,dy,f,harmonics)
            return (y-design(t,f,harmonics)@model['coefficients'])/(1 if dy is None else dy)
        except ValueError:
            return np.full(len(t),1e10)
    result=least_squares(residual,np.clip(starts,lo+1e-12*(hi-lo),hi-1e-12*(hi-lo)),bounds=(lo,hi),x_scale='jac',max_nfev=200,ftol=1e-10,xtol=1e-10,gtol=1e-10)
    if not result.success: raise ValueError('Joint frequency refinement did not converge')
    model=linear_fit(t,y,dy,sorted(result.x),harmonics)
    model['local_bound_hit']=bool(np.any(np.minimum(result.x-lo,hi-result.x)<1e-5*(hi-lo)))
    return model


def related(f,g,baseline,harmonics):
    # Protect against fitting the same spectral component in two different modes.
    return any(abs(k*f-j*g)<1/baseline for k in range(1,harmonics+1) for j in range(1,harmonics+1))


def seed_candidates(t,residual,dy,grid,harmonics,count):
    from analyze import peak_indices
    seeds=[]
    for terms in sorted(set([1,harmonics])):
        ls=LombScargle(t,residual,dy,nterms=terms)
        try: power=ls.power(grid,method='chi2')
        except np.linalg.LinAlgError:
            power=np.full(len(grid),np.nan)
            for i,f in enumerate(grid):
                try: power[i]=ls.power(f,method='chi2')
                except np.linalg.LinAlgError: pass
        power=np.where((power>=0)&(power<=1+1e-8),power,np.nan)
        for i in peak_indices(power,grid,np.ptp(t),False,count):
            for factor in (1.,.5,2.):
                f=float(grid[i]*factor)
                if __import__('analyze').grid_bounds(grid,f) is not None and all(abs(f-g)>.1/np.ptp(t) for g in seeds): seeds.append(f)
    return seeds


def discover(t,y,dy,grid,args):
    best=linear_fit(t,y,dy,[],args.harmonics)
    history=[dict(stage=0,accepted=True,**best)]
    for stage in range(1,args.max_modes+1):
        residual=y-design(t,best['frequencies'],args.harmonics)@best['coefficients']
        if np.std(residual)<1e-12*max(1.,np.std(y)): break
        candidates=[]
        for seed in seed_candidates(t,residual,dy,grid,args.harmonics,args.refine_candidates):
            if any(related(seed,g,np.ptp(t),args.harmonics) for g in best['frequencies']): continue
            try: model=refine(t,y,dy,best['frequencies']+[seed],grid,args.harmonics)
            except ValueError: continue
            fs=model['frequencies']
            if any(related(fs[i],fs[j],np.ptp(t),args.harmonics) for i in range(len(fs)) for j in range(i)): continue
            if any(np.max(np.abs(np.array(fs)-c['frequencies']))<.02/np.ptp(t) for c in candidates): continue
            candidates.append(model)
        if not candidates: break
        candidates.sort(key=lambda c:c['bic'])
        chosen=candidates[0]
        accept=best['bic']-chosen['bic']>=args.bic_improvement
        for rank,model in enumerate(candidates):
            history.append(dict(stage=stage,rank=rank+1,accepted=bool(accept and rank==0),delta_bic_to_stage_best=float(model['bic']-chosen['bic']),delta_bic_from_previous=float(model['bic']-best['bic']),**model))
        if not accept: break
        best=chosen
    return best,history


def advanced(t,y,dy,grid,args,out,signal_meta=None):
    if signal_meta is None:
        signal_meta={'signal_kind':args.signal_kind,'label':'V/R' if args.signal_kind=='vr' else 'Signal'}
    original_args=copy.copy(args)
    args=copy.copy(args)
    selection=None
    if args.auto_harmonics:
        args.harmonics,selection=select_harmonics(t,y,dy,grid,args)
        (out/'harmonic_selection.json').write_text(json.dumps(selection,indent=2),encoding='utf-8')
    print(f'Advanced: joint candidate refinement, H={args.harmonics}...',flush=True)
    best,history=discover(t,y,dy,grid,args)
    best['harmonics']=args.harmonics
    predicted=design(t,best['frequencies'],args.harmonics)@best['coefficients']
    residual=y-predicted
    records=[]
    for row in history:
        records.append({k:(json.dumps(v) if isinstance(v,list) else v) for k,v in row.items()})
    pd.DataFrame(records).to_csv(out/'joint_candidates.csv',index=False)
    pd.DataFrame({'time_days_from_epoch':t,'signal':y,'model':predicted,'residual':residual}).to_csv(out/'joint_residuals.csv',index=False)
    # Search and select mode count again within each training split.
    validation=[]
    for fold,(train,test) in enumerate(blocked_splits(len(t),args.cv_folds,args.cv_gap_points)):
        print(f'Advanced outer validation: {fold+1}/{args.cv_folds}',flush=True)
        fold_args=copy.copy(original_args)
        gain=None; model=None
        try:
            if args.auto_harmonics:
                fold_args.harmonics,_=select_harmonics(t[train],y[train],None if dy is None else dy[train],grid,fold_args)
            model,_=discover(t[train],y[train],None if dy is None else dy[train],grid,fold_args)
            pred=design(t[test],model['frequencies'],fold_args.harmonics)@model['coefficients']
            w=np.ones(len(test)) if dy is None else 1/dy[test]**2
            baseline=np.average(y[train],weights=None if dy is None else 1/dy[train]**2)
            denominator=np.sum(w*(y[test]-baseline)**2)
            if denominator>0: gain=float(1-np.sum(w*(y[test]-pred)**2)/denominator)
        except ValueError: pass
        validation.append(dict(fold=fold,harmonics=fold_args.harmonics,gain=gain,periods_days=[] if model is None else [1/f for f in model['frequencies']]))
    pd.DataFrame(validation).to_csv(out/'joint_validation.csv',index=False)
    # Global re-search for every generated dataset, including model-count selection.
    rng=np.random.default_rng(args.seed+8031)
    block_values,block_segments,block_info=residual_blocks(t,residual,dy,args.block_length)
    estimated_sigma=None; estimate_info=None
    if dy is None and args.noise_estimate=='difference' and args.uncertainty_mode=='iid':
        from uncertainties import difference_noise
        estimated_sigma,estimate_info=difference_noise(t,y)
    draws=[]; recovered=[[] for _ in best['frequencies']]; same_count=0
    for iteration in range(args.uncertainty_trials):
        if iteration%5==0: print(f'Advanced uncertainty: {iteration}/{args.uncertainty_trials}',flush=True)
        if estimated_sigma is not None:
            noise=rng.normal(size=len(t))*estimated_sigma
        else:
            noise=draw_blocks(block_values,block_segments,rng,dy) if args.uncertainty_mode=='block' else (rng.normal(size=len(t))*dy if dy is not None else rng.choice(residual-np.mean(residual),size=len(t),replace=True))
        model,_=discover(t,predicted+noise,dy,grid,args)
        fs=model['frequencies']; same_count+=len(fs)==len(best['frequencies'])
        match={}
        if fs and best['frequencies']:
            cost=np.abs(np.array(best['frequencies'])[:,None]-np.array(fs)[None,:])
            ii,jj=linear_sum_assignment(cost)
            for i,j in zip(ii,jj):
                if cost[i,j]<.5/np.ptp(t):
                    recovered[i].append(1/fs[j]); match[int(i)]=float(1/fs[j])
        draws.append(dict(iteration=iteration,mode_count=len(fs),periods_days=json.dumps([1/f for f in fs]),matched_periods=json.dumps(match)))
    pd.DataFrame(draws,columns=['iteration','mode_count','periods_days','matched_periods']).to_csv(out/'joint_uncertainty_samples.csv',index=False)
    modes=[]
    for i,f in enumerate(best['frequencies']):
        values=recovered[i]
        row=dict(mode=i+1,frequency_per_day=f,period_days=1/f,cycles=float(np.ptp(t)*f),matched_trials=len(values),
                 recovery_fraction=len(values)/args.uncertainty_trials if args.uncertainty_trials else None,
                 near_search_boundary=bool(min(abs(f-grid[0]),abs(f-grid[-1]))<1/np.ptp(t)))
        if len(values)>=10:
            row.update(zip(['conditional_p16_days','conditional_median_days','conditional_p84_days'],map(float,np.percentile(values,[16,50,84]))))
        modes.append(row)
    pd.DataFrame(modes,columns=['mode','frequency_per_day','period_days','cycles','matched_trials','recovery_fraction','near_search_boundary','conditional_p16_days','conditional_median_days','conditional_p84_days']).to_csv(out/'joint_periods.csv',index=False)
    gains=[r['gain'] for r in validation if r['gain'] is not None]
    summary=dict(scope='original_valid_data_before_optional_clipping',family='joint_stationary_harmonic_regression',model=best,modes=modes,
                 signal_kind=signal_meta['signal_kind'],signal_label=signal_meta['label'],
                 measurement_error_model=signal_meta.get('error_model'),noise_estimate=estimate_info,
                 selected_harmonics=args.harmonics,harmonic_selection=selection,
                 residual_dependence=block_info,validation=validation,mean_prediction_gain=float(np.mean(gains)) if gains else None,
                 status='candidate_model' if modes else 'no_supported_periodic_model',
                 uncertainty_trials=args.uncertainty_trials,noise_model='segmented_circular_residual_blocks' if args.uncertainty_mode=='block' else ('estimated_difference_mad_gaussian_noise' if estimated_sigma is not None else 'independent_gaussian_measurement_errors' if dy is not None else 'iid_resampled_centered_residuals'),
                 same_mode_count_fraction=same_count/args.uncertainty_trials if args.uncertainty_trials else None,
                 limitations=['Bootstrap holds selected harmonic complexity fixed; selection uncertainty is not included.',
                              'Nested validation reselects harmonics in each outer training split when auto-harmonics is enabled.',
                              'Sequential multi-start search is not an exhaustive global model search.',
                              'BIC threshold is a selection heuristic, not a false-alarm probability.',
                              'Percentiles are conditional on matching the original frequency basin and the assumed noise model; not calibrated confidence intervals.',
                              'Independent-mode pairs with overlapping harmonic frequencies within 1/T are not resolved.',
                              'Block validation is internal, not validation on a new observing campaign.',
                              'Stationary harmonic models do not identify pulsation origin or model drifting periods / red noise.'])
    if modes and (len(gains)<args.cv_folds or np.mean(gains)<=0): summary['status']='not_validated_out_of_sample'
    if args.uncertainty_trials<100: summary['limitations'].append('Fewer than 100 simulations: uncertainty results are exploratory.')
    summary['close_alternative_count'] = sum(1 for row in history if row['stage']==len(modes) and not row['accepted'] and row.get('delta_bic_to_stage_best',float('inf'))<2) if modes else 0
    if getattr(args,'search_origin','manual')=='discovery':
        summary['limitations'].insert(0,'Candidate windows were selected on the entire input; internal folds do not independently validate that selection. Simulations hold windows fixed.')
        summary['status']='conditional_on_data_selected_windows' if modes else summary['status']
    if args.validation_input:
        summary['external_validation'] = external_validation(t,y,best,args,out)
    (out/'advanced.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    # Relationships between refined alternatives and window peaks are diagnostics,
    # never a claim that a candidate has been proved to be an alias.
    first=[h for h in history if h['stage']==1][:10]
    relations=[]
    for i,a in enumerate(first):
        for b in first[:i]:
            fa=a['frequencies'][0]; fb=b['frequencies'][0]
            ratio=max(fa,fb)/min(fa,fb)
            difference=abs(fa-fb)
            window=float(abs(np.mean(np.exp(2j*np.pi*difference*t)))**2)
            relations.append(dict(period_a=1/fa,period_b=1/fb,frequency_ratio=ratio,
                                 near_integer_harmonic=bool(any(abs(max(fa,fb)-k*min(fa,fb))<1/np.ptp(t) for k in (2,3,4))),
                                 window_at_frequency_difference=window))
    pd.DataFrame(relations,columns=['period_a','period_b','frequency_ratio','near_integer_harmonic','window_at_frequency_difference']).to_csv(out/'candidate_relations.csv',index=False)
    from matplotlib import pyplot as plt
    fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True)
    axes[0].plot(t,y,'.',label='observed'); axes[0].plot(t,predicted,'.',label='joint model'); axes[0].legend()
    axes[1].plot(t,residual,'.'); axes[1].axhline(0,color='gray',lw=.8)
    axes[0].set_ylabel(signal_meta['label']); axes[1].set(ylabel='Residual',xlabel='Time from epoch (days)')
    fig.tight_layout(); fig.savefig(out/'joint_fit.png',dpi=160); plt.close(fig)
    lines=['# Refinement and joint period model','',f"Status: {summary['status']}",
           f"Number of components: {len(modes)}; mean prediction gain: {summary['mean_prediction_gain']}",'',
           '| Component | Period, days | Recovery fraction | Conditional p16-p84, days |','|---|---:|---:|---|']
    for row in modes: lines.append(f"| {row['mode']} | {row['period_days']:.10g} | {row['recovery_fraction']} | {row.get('conditional_p16_days','—')} – {row.get('conditional_p84_days','—')} |")
    lines+=['','Data before optional clipping. This is a candidate model, not evidence of physical pulsation.',
            'Percentiles are conditional on recovery of the original frequency peak. Inspect recovery fractions, changes in component count and alternatives in joint_candidates.csv.',
            'Time-block validation is internal; it does not provide new independent observations.',
            'Algorithm, thresholds and limitations: README.md. Full numerical results: advanced.json.']
    if getattr(args,'search_origin','manual')=='discovery':lines.insert(2,'DATA-SELECTED WINDOWS: internal validation and simulations are conditional; broad screening is not repeated in folds or simulations.')
    lines += ['', 'Noise source in simulations: '+summary['noise_model']+'. Measurement errors and noise estimates are not period uncertainties.']
    if estimate_info is not None:
        lines.append('Approximate common noise: '+str(estimated_sigma)+' in signal units; not an instrumental error.')
    if signal_meta['signal_kind']=='vr':
        lines[0]='# Joint model of V/R periodicity'
        lines.insert(2,'Spectroscopic V/R: periods of intensity-ratio variation, not confirmed pulsation periods.')
    if 'external_validation' in summary:
        external=summary['external_validation']
        lines += ['', f"External validation file: {external['points']} points; prediction gain {external['prediction_gain']:.6g}; RMSE {external['rmse']:.6g}. No fitting was performed on the validation file."] if external['prediction_gain'] is not None else ['', 'Prediction gain is undefined for the external validation file; see advanced.json.']
    (out/'advanced.md').write_text('\n'.join(lines),encoding='utf-8')
    return summary


def external_validation(t,y,model,args,out):
    """Predict an independently supplied table without fitting or tuning on it."""
    import copy
    import hashlib
    from pathlib import Path
    from analyze import load_data
    path=Path(args.validation_input)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest==hashlib.sha256(Path(args.input).read_bytes()).hexdigest():
        raise ValueError('Validation file is identical to training data.')
    _,train_y,train_dy,_,train_meta=load_data(args)
    other=copy.copy(args); other.input=str(path)
    vt,vy,vdy,excluded,meta=load_data(other)
    if meta['signal_kind']!=train_meta['signal_kind'] or meta['label']!=train_meta['label']:
        raise ValueError('Training and validation signal labels/kinds differ; harmonize units explicitly.')
    factor={'days':1.,'hours':24.,'minutes':1440.,'seconds':86400.}[args.time_unit]
    vt=vt+(meta['epoch_input_units']-train_meta['epoch_input_units'])/factor
    # Exact duplicate observations cannot count as independent validation.
    pairs=set(zip(t,y))
    if any((float(tx),float(yx)) in pairs for tx,yx in zip(vt,vy)):
        raise ValueError('Validation contains duplicated training observations.')
    prediction=design(vt,model['frequencies'],model.get('harmonics',args.harmonics))@model['coefficients']
    residual=vy-prediction
    weights=np.ones(len(vt)) if vdy is None else 1/vdy**2
    denominator=float(np.sum(weights*(vy-np.average(train_y,weights=None if train_dy is None else 1/train_dy**2))**2))
    gain=float(1-np.sum(weights*residual**2)/denominator) if denominator>0 else None
    pd.DataFrame({'time_days_from_training_epoch':vt,'signal':vy,'prediction':prediction,'residual':residual}).to_csv(out/'external_validation.csv',index=False)
    excluded.to_csv(out/'external_validation_excluded.csv',index=False)
    return dict(input=str(path),sha256=digest,points=len(vt),prediction_gain=gain,rmse=float(np.sqrt(np.mean(residual**2))),
                refitted=False,error_model=meta.get('error_model'),epoch_input_units=meta['epoch_input_units'],note='Independence, photometric calibration and time standards must be established from data provenance.')
'''

# ROBUSTNESS - complete embedded application module
ROBUSTNESS_SOURCE = r'''"""Training-only complexity selection and segmented circular residual bootstrap."""
import copy
import numpy as np


def blocked_splits(n, folds, gap=0):
    indices = np.arange(n)
    for test in np.array_split(indices, folds):
        if not len(test):
            continue
        train = indices[(indices < test[0] - gap) | (indices > test[-1] + gap)]
        yield train, test


def select_harmonics(t, y, dy, grid, args):
    from advanced import discover, design
    rows = []
    for h in range(1, args.max_harmonics + 1):
        trial = copy.copy(args)
        trial.harmonics = h
        losses = []
        for train, test in blocked_splits(len(t), args.harmonic_folds, args.cv_gap_points):
            try:
                model, _ = discover(t[train], y[train], None if dy is None else dy[train], grid, trial)
                prediction = design(t[test], model['frequencies'], h) @ model['coefficients']
                loss = np.average((y[test] - prediction)**2, weights=None if dy is None else 1/dy[test]**2)
                if np.isfinite(loss):
                    losses.append(float(loss))
            except (ValueError, np.linalg.LinAlgError):
                pass
        valid = len(losses) == args.harmonic_folds
        rows.append(dict(harmonics=h, valid_folds=len(losses), fold_mse=losses,
                         mean_mse=float(np.mean(losses)) if valid else None,
                         se_mse=float(np.std(losses, ddof=1)/np.sqrt(len(losses))) if valid else None))
        print(f'Harmonic selection: H={h}, CV MSE={rows[-1]["mean_mse"]}', flush=True)
    eligible = [r for r in rows if r['mean_mse'] is not None]
    if not eligible:
        raise ValueError('No harmonic complexity has valid predictions in every selection fold')
    winner = min(eligible, key=lambda r: r['mean_mse'])
    threshold = winner['mean_mse'] + winner['se_mse']
    selected = min(r['harmonics'] for r in eligible if r['mean_mse'] <= threshold)
    return selected, dict(selected_harmonics=selected, candidates=rows, threshold_mse=threshold,
                         rule='simplest within one standard error of minimum fold MSE; heuristic with correlated folds',
                         selection_folds=args.harmonic_folds, gap_points=args.cv_gap_points)


def residual_blocks(t, residual, dy=None, requested_length=0, gap_factor=5.):
    """Estimate block length per contiguous segment; no samples cross observing gaps."""
    dt = np.diff(t)
    positive = dt[dt > 0]
    cadence = float(np.median(positive)) if len(positive) else 0.
    splits = np.flatnonzero(dt > gap_factor*cadence) + 1 if cadence else []
    segments = np.split(np.arange(len(t)), splits)
    standardized = np.asarray(residual) / (1 if dy is None else dy)
    # Preserve slow segment offsets in the resampling distribution; center globally.
    standardized = standardized - np.mean(standardized)
    metadata = []
    for indices in segments:
        x = standardized[indices]
        z = x - np.mean(x)
        denominator = np.dot(z, z)
        cap = max(1, len(x)//4)
        lag = 1
        if denominator > 0:
            for lag in range(1, cap + 1):
                if np.dot(z[:-lag], z[lag:])/denominator <= np.exp(-1):
                    break
        length = min(len(x), requested_length) if requested_length else min(cap, max(int(np.ceil(len(x)**(1/3))), lag))
        correlation = float(np.corrcoef(x[:-1], x[1:])[0, 1]) if len(x)>2 and np.std(x[:-1])>0 and np.std(x[1:])>0 else None
        metadata.append(dict(start=int(indices[0]), stop=int(indices[-1]+1), points=len(x), block_length=int(length), lag1_correlation=correlation))
    return standardized, metadata, dict(method='segmented_circular_residual_blocks', segments=metadata,
        median_cadence_days=cadence, gap_factor=gap_factor, standardized_by_errors=dy is not None,
        length_rule='explicit' if requested_length else 'max(cube-root n, first ACF <= 1/e), capped at n/4 per segment',
        warning='Point-index blocks approximate time correlation; length heuristic and conditional percentiles are not calibrated coverage.')


def draw_blocks(standardized, segments, rng, dy=None):
    noise = np.empty(len(standardized))
    for segment in segments:
        start, stop, length = segment['start'], segment['stop'], segment['block_length']
        n = stop-start
        origins = rng.integers(0, n, size=int(np.ceil(n/length)))
        indices = ((origins[:, None]+np.arange(length)) % n).ravel()[:n]
        noise[start:stop] = standardized[start:stop][indices]
    return noise * (1 if dy is None else dy)
'''

# UNCERTAINTIES - complete embedded application module
UNCERTAINTIES_SOURCE = r'''"""Explicit uncertainty provenance; empirical noise is never a measured error."""
import numpy as np
import pandas as pd


def difference_noise(t, y, gap_factor=5.):
    dt=np.diff(t)
    positive=dt[dt>0]
    if not len(positive): raise ValueError('Noise estimate requires distinct observation times.')
    cadence=float(np.median(positive))
    keep=(dt>0)&(dt<=gap_factor*cadence)
    differences=np.diff(y)[keep]
    if len(differences)<8: raise ValueError('Too few adjacent pairs for an empirical noise estimate (need 8).')
    sigma=float(1.4826*np.median(np.abs(differences-np.median(differences)))/np.sqrt(2))
    if not np.isfinite(sigma) or sigma<=np.finfo(float).eps*max(1.,np.max(np.abs(y))):
        raise ValueError('Difference-MAD noise is zero or numerically unresolved; supply errors instead.')
    return sigma,dict(source='estimated_difference_mad',sigma=sigma,pairs_used=int(keep.sum()),
        pairs_excluded=int((~keep).sum()),max_pair_gap_days=gap_factor*cadence,
        instrumental=False,assumptions='Equal white-noise scale; intrinsic change between adjacent observations is small.',
        limitations='Variability can inflate this estimate; positive noise correlation can reduce it. Irregular cadence and sparse sampling may invalidate it. Not per-point instrumental errors.')


def propagate_vr(df, args, signal_column):
    names=[getattr(args,n,None) for n in ('vr_v_col','vr_r_col','vr_v_error_col','vr_r_error_col')]
    rho=getattr(args,'vr_error_correlation',0.)
    if not any(names):
        if rho!=0: raise ValueError('V/R error correlation requires component columns.')
        return df,None
    if not all(names) or args.signal_kind!='vr':
        raise ValueError('V/R propagation requires --signal-kind vr and all four V/R component columns.')
    if len(set(names))!=4 or signal_column in names:
        raise ValueError('Ratio, component values and component error columns must be distinct.')
    if not np.isfinite(rho) or not -1<=rho<=1: raise ValueError('V/R error correlation must be in [-1,1].')
    if any(n not in df for n in names): raise ValueError('Missing V/R component column.')
    v,r,sv,sr=[pd.to_numeric(df[n],errors='coerce').to_numpy(float) for n in names]
    valid=np.isfinite(v)&np.isfinite(r)&np.isfinite(sv)&np.isfinite(sr)&(v>0)&(r>0)&(sv>0)&(sr>0)
    with np.errstate(divide='ignore',invalid='ignore',over='ignore'):
        ratio=v/r
        variance=(sv/r)**2+(v*sr/r**2)**2-2*rho*v*sv*sr/r**3
    observed=pd.to_numeric(df[signal_column],errors='coerce').to_numpy(float)
    # Permit original three-decimal rounding, never silently pair unrelated errors and signal.
    if np.any(valid & np.isfinite(observed) & ~np.isclose(observed,ratio,rtol=.005,atol=.0005)):
        raise ValueError('Signal does not agree with V/R components; check normalization and columns.')
    sigma=np.where(valid & np.isfinite(variance) & (variance>0),np.sqrt(np.maximum(variance,0)),np.nan)
    key='__propagated_vr_error__'
    if key in df: raise ValueError('Reserved propagated error column already exists.')
    result=df.copy();result[key]=sigma
    return result,dict(source='propagated_vr',column=key,component_columns=names,correlation=float(rho),
        formula='var(V/R)=(sigmaV/R)^2+(V*sigmaR/R^2)^2-2*rho*V*sigmaV*sigmaR/R^3',
        high_relative_component_error_rows=int(np.sum(valid & ((sv>0.2*v)|(sr>0.2*r)))),
        assumptions='First-order propagation; rho=0 assumes uncorrelated component errors. Shared normalization may correlate them. Large relative errors require a nonlinear treatment.')


def method_error_usage(methods, has_errors, perturbations):
    return {name:dict(fit_weights='inverse_variance' if has_errors and name in ('ls','fourier') else ('temporal_only' if name=='wwz' else 'equal'),
        error_perturbations=bool(perturbations),
        note='PDM statistic is unweighted.' if name=='pdm' else ('WWZ uses temporal localization, not measurement-error weights.' if name=='wwz' else 'Supplied or propagated errors enter the weighted fit; estimated common noise does not change fit weights.')) for name in methods}
'''

# DISCOVERY - complete embedded application module
DISCOVERY_SOURCE = r'''"""Explicit broad reconnaissance and candidate-window proposals.

A fast LS / two-harmonic screen is a selection stage, not validation.
"""
import math
import numpy as np
import pandas as pd
from astropy.timeseries import LombScargle


def merge_windows(windows):
    result=[]
    for lo,hi in sorted(windows):
        if result and lo<=result[-1][1]:result[-1][1]=max(hi,result[-1][1])
        else:result.append([float(lo),float(hi)])
    return result


def _screen_power(model,grid,terms):
    try:
        return model.power(grid,method=('fast' if terms==1 else 'fastchi2') if len(grid)>10 else 'chi2',**({'assume_regular_frequency':True} if len(grid)>10 else {}))
    except np.linalg.LinAlgError:
        if len(grid)>512:
            mid=len(grid)//2
            return np.r_[_screen_power(model,grid[:mid],terms),_screen_power(model,grid[mid:],terms)]
        result=np.full(len(grid),np.nan)
        for i,f in enumerate(grid):
            try:result[i]=model.power(f,method='chi2')
            except np.linalg.LinAlgError:pass
        return result


def scout(t,y,dy,min_period,max_period,out=None,samples_per_peak=5,max_points=3000000,top_count=5):
    from analyze import peak_indices
    baseline=float(np.ptp(t))
    if not (np.isfinite(min_period) and np.isfinite(max_period) and 0<min_period<max_period and baseline>0):
        raise ValueError('Scout requires finite positive ordered period bounds and a positive baseline.')
    # Two harmonics: account for their narrower frequency peaks. No cadence cutoff.
    count=max(3,math.ceil((1/min_period-1/max_period)*baseline*samples_per_peak*2)+1)
    if count>max_points:
        raise ValueError(f'Scout needs {count:,} frequencies (limit {max_points:,}). Choose explicit narrower bounds or deliberately raise --scout-max-points. Resolution is not silently reduced.')
    frequencies=np.linspace(1/max_period,1/min_period,count)
    records=[];spectra={}
    for terms in (1,2):
        model=LombScargle(t,y,dy,nterms=terms)
        score=np.empty(count)
        for start in range(0,count,100000):
            stop=min(start+100000,count)
            print(f'Scout H={terms}: {stop:,}/{count:,} frequencies',flush=True)
            grid=frequencies[start:stop]
            score[start:stop]=_screen_power(model,grid,terms)
        score=np.where(np.isfinite(score),score,np.nan)
        spectra[f'H{terms}']=score
        # Recheck more candidates than we retain using the exact solver; fast FFT powers are approximate.
        seeds=peak_indices(score,frequencies,baseline,count=max(30,top_count*6))
        exact=[]
        for i in seeds:
            lo=max(frequencies[0],frequencies[i]-1/baseline)
            hi=min(frequencies[-1],frequencies[i]+1/baseline)
            local=np.linspace(lo,hi,161)
            try:power=model.power(local,method='chi2')
            except np.linalg.LinAlgError:continue
            good=np.where(np.isfinite(power)&(power>=-1e-8)&(power<=1+1e-8),power,-np.inf)
            j=int(np.argmax(good))
            if not np.isfinite(good[j]):continue
            exact.append(dict(harmonics=terms,frequency_per_day=float(local[j]),period_days=float(1/local[j]),power=float(good[j]),near_scout_boundary=bool(min(local[j]-frequencies[0],frequencies[-1]-local[j])<1/baseline)))
        kept=[]
        for row in sorted(exact,key=lambda r:r['power'],reverse=True):
            if all(abs(row['frequency_per_day']-r['frequency_per_day'])>=1/baseline for r in kept):
                row['rank_within_model']=len(kept)+1;kept.append(row)
            if len(kept)>=top_count:break
        records.extend(kept)
    if not records:raise ValueError('Scout found no finite supported peaks. Inspect data and bounds.')
    windows=[]
    for row in records:
        for factor in (1.,.5,2.):
            center=row['frequency_per_day']*factor
            if frequencies[0]<=center<=frequencies[-1]:
                windows.append([max(frequencies[0],center-4/baseline),min(frequencies[-1],center+4/baseline)])
    windows=merge_windows(windows)
    relations=[]
    for i,a in enumerate(records):
        for b in records[:i]:
            fa,fb=a['frequency_per_day'],b['frequency_per_day'];delta=abs(fa-fb)
            if delta<1/baseline:continue
            relations.append(dict(period_a_days=a['period_days'],period_b_days=b['period_days'],
                                  possible_integer_harmonic=any(abs(max(fa,fb)-k*min(fa,fb))<1/baseline for k in (2,3,4)),
                                  window_at_frequency_difference=float(abs(np.mean(np.exp(2j*np.pi*delta*t)))**2)))
    result=dict(mode='discovery',min_period_days=min_period,max_period_days=max_period,frequency_count=count,
                sampling_per_peak=samples_per_peak,scout_harmonics=[1,2],candidate_count_per_model=top_count,
                window_half_width_in_1_over_T=4,frequency_windows=windows,candidates=records,
                limitations=['Only the declared finite range was screened; periods outside it remain untested.',
                'LS and H=2 screening can miss variability favored by other model families; it is not a global four-method search.',
                'Candidate windows were selected using these same data. Subsequent validation and Monte Carlo are conditional on the fixed windows, not independent confirmation.',
                'Harmonic companions at half and twice each seed frequency are included only within the declared broad range.',
                'Window-function relationships are alias diagnostics, not proof of aliasing.'])
    if out is not None:
        from matplotlib import pyplot as plt
        pd.DataFrame(records).to_csv(out/'scout_candidates.csv',index=False)
        pd.DataFrame(relations,columns=['period_a_days','period_b_days','possible_integer_harmonic','window_at_frequency_difference']).to_csv(out/'scout_alias_diagnostics.csv',index=False)
        # Envelope downsampling preserves narrow peaks in a display, but not every evaluated frequency.
        display=set([0,count-1])
        for score in spectra.values():
            for start in range(0,count,max(1,math.ceil(count/6000))):
                block=score[start:start+max(1,math.ceil(count/6000))]
                if np.isfinite(block).any():display.add(start+int(np.nanargmax(block)))
        ids=np.array(sorted(display))
        pd.DataFrame({'frequency_per_day':frequencies[ids],**{k:v[ids] for k,v in spectra.items()}}).to_csv(out/'scout_plot_envelope.csv',index=False)
        fig,axes=plt.subplots(2,1,figsize=(11,7))
        for terms,ax in zip((1,2),axes):
            ax.plot(1/frequencies[ids],spectra[f'H{terms}'][ids],lw=.7)
            for row in records:
                if row['harmonics']==terms:ax.axvline(row['period_days'],color='darkorange',alpha=.45,lw=.8)
            ax.set(xscale='log',xlabel='Period (days)',ylabel='Normalized power',title=f'Broad scout H={terms}: peak-preserving display envelope')
            ax.grid(alpha=.25)
        fig.tight_layout();fig.savefig(out/'scout_periodograms.png',dpi=140);plt.close(fig)
    return result
'''

# PRESENTATION - complete embedded application module
PRESENTATION_SOURCE = r'''"""Plots and explicit candidate summaries for the standalone tool."""
import json
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

NAMES={'ls':'Lomb-Scargle','fourier':'Multiharmonic Fourier regression','pdm':'Phase Dispersion Minimization','wwz':'Weighted Wavelet Z-transform'}


def plot_method_results(out,t,y,dy,f,window,spectra,rows,meta,args):
    from analyze import grid_segments,peak_indices
    segments=grid_segments(f)
    for method,score in spectra.items():
        fig,ax=plt.subplots(figsize=(11,4.5))
        for ids in segments:ax.plot(1/f[ids],score[ids],color='tab:blue',lw=.9)
        row=next(r for r in rows if r['method']==method)
        if row.get('period_days') is not None:
            period=row['period_days']
            ax.axvline(period,color='tab:orange',ls='--',label=f'Leading candidate: {period:.9g} d = {period*1440:.7g} min')
            alternatives=peak_indices(score,f,float(np.ptp(t)),method=='pdm',3)[1:]
            for i in alternatives:ax.axvline(1/f[i],color='gray',ls=':',alpha=.65)
            ax.legend(loc='best',fontsize=9)
        else:ax.text(.5,.5,'Insufficient support: no period estimate',transform=ax.transAxes,ha='center')
        ylabel='Theta (minimum is preferred)' if method=='pdm' else ('WWZ (maximum is preferred)' if method=='wwz' else 'Normalized power (maximum is preferred)')
        ax.set(xlabel='Period (days)',ylabel=ylabel,title=NAMES[method]+' periodogram')
        if args.max_period/args.min_period>100:ax.set_xscale('log')
        if len(segments)>1:ax.text(.01,.02,'Only selected windows are evaluated; blank gaps are unsearched.',transform=ax.transAxes,fontsize=9,bbox=dict(facecolor='white',alpha=.85))
        ax.grid(alpha=.25);fig.tight_layout();fig.savefig(out/(method+'_periodogram.png'),dpi=150);plt.close(fig)
        # Narrow panels show peaks which are invisible on a very broad linear axis.
        best=peak_indices(score,f,float(np.ptp(t)),method=='pdm',3)
        if best:
            fig,axes=plt.subplots(len(best),1,figsize=(10,3*len(best)),squeeze=False)
            for rank,(idx,ax) in enumerate(zip(best,axes[:,0]),1):
                local=np.abs(f-f[idx])<=4/np.ptp(t)
                for ids in segments:
                    sub=ids[local[ids]]
                    if len(sub):ax.plot(1/f[sub]*1440,score[sub],color='tab:blue',lw=1)
                ax.axvline(1440/f[idx],color='tab:orange',ls='--')
                ax.set(xlabel='Period (minutes)',ylabel=('Theta' if method=='pdm' else 'WWZ' if method=='wwz' else 'Power'),title=f'{NAMES[method]} candidate {rank}: {1/f[idx]:.10g} days')
                ax.grid(alpha=.25)
            fig.tight_layout();fig.savefig(out/(method+'_peak_details.png'),dpi=140);plt.close(fig)
    # A sampling-window diagnostic at low frequencies complements window values at periodogram frequencies.
    wf=np.linspace(1/np.ptp(t),max(2.1,2/np.ptp(t)),min(20000,max(500,round(np.ptp(t)*5))))
    wp=np.empty(len(wf))
    for start in range(0,len(wf),256):wp[start:start+256]=abs(np.exp(2j*np.pi*wf[start:start+256,None]*t).mean(axis=1))**2
    fig,ax=plt.subplots(figsize=(10,3.5));ax.plot(wf,wp,lw=.7)
    ax.set(xlabel='Frequency (cycles/day)',ylabel='Window power',title='Observing-window diagnostic (finite sampled grid)');ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'sampling_window.png',dpi=140);plt.close(fig)
    pd.DataFrame({'frequency_per_day':wf,'window_power':wp}).to_csv(out/'sampling_window.csv',index=False)
    path=out/'perturbation_periods.csv'
    if args.bootstrap and path.exists():
        draws=pd.read_csv(path)
        summaries=[]
        for row in rows:
            method=row['method'];summary={k:v for k,v in row.items() if k.startswith(('monte_carlo','perturbation','same_peak','conditional_peak'))}
            summary.update(method=method,trials_requested=args.bootstrap,noise_scope='Independent Gaussian perturbations around retained measured values; fixed clipping and fixed search windows.')
            summaries.append(summary)
            values=draws.loc[draws.method==method,'period_days'].dropna().to_numpy()
            fig,ax=plt.subplots(figsize=(10,4))
            if len(values):
                ax.hist(values*1440,bins=min(30,max(5,int(np.sqrt(len(values))))),color='steelblue',alpha=.85)
                ax.axvline(row['period_days']*1440,color='darkorange',ls='--',label='Original leading candidate');ax.legend()
            else:ax.text(.5,.5,'No supported Monte Carlo estimates',transform=ax.transAxes,ha='center')
            from matplotlib.ticker import MaxNLocator
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set(xlabel='Recovered period (minutes)',ylabel='Repetitions',title=f"{NAMES[method]} Monte Carlo: {len(values)}/{args.bootstrap} supported repetitions")
            fig.tight_layout();fig.savefig(out/(method+'_monte_carlo.png'),dpi=140);plt.close(fig)
        pd.DataFrame(summaries).to_csv(out/'monte_carlo_summary.csv',index=False)
        (out/'MONTE_CARLO.md').write_text('# Monte Carlo measurement perturbations\n\nEach selected supported method repeats its period search over the ENTIRE selected frequency grid for each draw. This is sensitivity to assumed independent Gaussian measurement errors, not a false-alarm probability or calibrated confidence interval.\n\nClipping, candidate windows and harmonic settings are held fixed. Broad discovery is not repeated; uncertainty outside selected windows is not assessed. The same random perturbations are shared across methods.\n\nThe same-peak fraction uses all requested trials as denominator; failures count against recovery. Global percentiles may span aliases; conditional peak percentiles exclude other peaks and must be read with the recovery fraction. Fewer than 100 repetitions are only a functional/exploratory check.\n\nPDM remains unweighted and WWZ uses temporal weights, but both receive the simulated measurements. If empirical difference noise was selected, it is a heuristic noise scale, not measured instrumental uncertainty.\n',encoding='utf-8')


def final_candidates(out,payload):
    records=[]
    try:peaks=pd.read_csv(out/'top_candidates.csv')
    except pd.errors.EmptyDataError:peaks=pd.DataFrame(columns=['method','rank','period_days'])
    for row in payload['results']:
        method=row['method']
        if row.get('period_days') is None:continue
        subset=peaks.loc[peaks.method==method].head(3)
        for _,peak in subset.iterrows():
            records.append(dict(method=method,rank=int(peak['rank']),period_days=float(peak.period_days),period_minutes=float(peak.period_days*1440),
                                scope='retained_after_clipping',status='leading_candidate' if peak['rank']==1 else 'alternative',
                                near_boundary=row['near_boundary'] if peak['rank']==1 else None,
                                same_peak_fraction=row.get('same_peak_fraction') if peak['rank']==1 else None))
    for row in payload.get('advanced',{}).get('modes',[]):
        records.append(dict(method='refined_joint_model',rank=row['mode'],period_days=row['period_days'],period_minutes=row['period_days']*1440,
                            scope='original_before_clipping',status=payload['advanced']['status'],near_boundary=None,same_peak_fraction=row.get('recovery_fraction')))
    columns=['method','rank','period_days','period_minutes','scope','status','near_boundary','same_peak_fraction']
    pd.DataFrame(records,columns=columns).to_csv(out/'FINAL_PERIODS.csv',index=False)
    decision=payload.get('recommendation',{}).get('decision',{})
    summary=dict(status=decision.get('status','candidates_only_no_validated_unique_winner') if records else 'no_supported_period',
                 preferred_method=decision.get('method'),preferred_period_days=decision.get('period_days'),
                 search_origin=payload['parameters'].get('search_origin','manual'),candidates=records,
                 note='Leading periods maximize each method statistic (minimize PDM theta). They are alternatives, not necessarily simultaneous independent modes. Agreement between methods is not independent confirmation.')
    (out/'FINAL_RESULT.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('\nFINAL PERIOD CANDIDATES (not guaranteed physical periods):',flush=True)
    for r in records:
        if r['rank']==1 or r['method']=='refined_joint_model':print(f"  {r['method']}: {r['period_days']:.10g} d = {r['period_minutes']:.8g} min [{r['scope']}]",flush=True)
    print('Decision: '+summary['status'],flush=True)
    return summary
'''

import sys
import json
import hashlib
import importlib.abc
import importlib.util
from pathlib import Path

EMBEDDED_SOURCES = {
    'analyze': ANALYZE_SOURCE,
    'recommendation': RECOMMENDATION_SOURCE,
    'advanced': ADVANCED_SOURCE,
    'robustness': ROBUSTNESS_SOURCE,
    'uncertainties': UNCERTAINTIES_SOURCE,
    'discovery': DISCOVERY_SOURCE,
    'presentation': PRESENTATION_SOURCE,
}


class _EmbeddedModules(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Load the explicitly listed application modules directly from memory."""
    def find_spec(self, fullname, path=None, target=None):
        if fullname in EMBEDDED_SOURCES:
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.__file__ = str(Path(__file__).resolve())
        exec(compile(EMBEDDED_SOURCES[module.__name__],
                     str(Path(__file__).resolve()) + ':' + module.__name__, 'exec'),
             module.__dict__)


def _activate_modules():
    # Avoid accidentally reusing neighboring or previously imported project modules.
    conflicts = [name for name in EMBEDDED_SOURCES if name in sys.modules
                 and not isinstance(getattr(sys.modules[name], '__loader__', None), _EmbeddedModules)]
    if conflicts:
        raise RuntimeError('Application module name conflict: '+', '.join(conflicts)+'. Run this file in a fresh Python process.')
    if not any(isinstance(finder, _EmbeddedModules) for finder in sys.meta_path):
        sys.meta_path.insert(0, _EmbeddedModules())


def _ask(prompt, default=None):
    answer=input(prompt + (f' [{default}]' if default is not None else '') + ': ').strip()
    return answer or default


APP_ROOT=Path(__file__).resolve().parent


def input_files():
    folder=APP_ROOT/'UPLOAD_DATA_HERE'
    folder.mkdir(exist_ok=True)
    return sorted((p for p in folder.iterdir() if p.is_file() and
                   p.suffix.lower() in ('','.csv','.tsv','.txt','.dat','.fits','.fit','.fts')),
                  key=lambda p:p.name.lower())


def select_input(interactive=False):
    files=input_files()
    if not files: raise ValueError('No observation tables in UPLOAD_DATA_HERE. Put a table there, then run again.')
    if len(files)==1:
        print('Input from UPLOAD_DATA_HERE: '+files[0].name)
        return files[0]
    if not interactive:
        raise ValueError('Several tables in UPLOAD_DATA_HERE. Use --input PATH or run without arguments to choose: '+', '.join(p.name for p in files))
    print('Observation tables in UPLOAD_DATA_HERE:')
    for i,p in enumerate(files,1): print(f'  {i}. {p.name}')
    choice=_ask('Choose the file number')
    try: index=int(choice)-1
    except (ValueError,TypeError):raise ValueError('Enter a listed file number.')
    if index<0 or index>=len(files):raise ValueError('File number outside the list.')
    return files[index]


def _positive_number(prompt,default=None):
    import math
    while True:
        try:value=float(_ask(prompt,default))
        except (ValueError,TypeError):print('Enter a positive number.');continue
        if math.isfinite(value) and value>0:return value
        print('Enter a finite positive number.')


def _period_factor(unit):
    factors={'minutes':1/1440,'hours':1/24,'days':1.}
    if unit not in factors:raise ValueError('Period unit must be minutes, hours or days.')
    return factors[unit]


def _wizard_args(argv):
    import analyze
    flags=('--basic','--preprocess-only','--step-by-step','--open-report','--no-clip','--no-recommend')
    clean=[x for x in argv if x not in flags]
    # Ranges are placeholders for loading only, never searched here.
    args=analyze.parser().parse_args(clean+['--min-period','.1','--max-period','1'])
    if '--basic' not in argv:args.advanced=True;args.auto_harmonics=True
    return args


def create_search_plan(args,t,y,dy,meta,mode,exposure=None,prior=None):
    from datetime import datetime,timezone
    import html
    from matplotlib import pyplot as plt
    from discovery import scout
    root=Path(args.output_dir)/datetime.now(timezone.utc).strftime('search_%Y%m%dT%H%M%S_%fZ')
    root.mkdir(parents=True,exist_ok=False)
    advice=dict(schema_version=2,mode=mode,object_name=args.object_name,
                input_sha256=hashlib.sha256(Path(args.input).read_bytes()).hexdigest(),
                input_time_unit=args.time_unit,baseline_days=float(t.max()-t.min()),valid_rows=len(t),
                exposure_seconds=exposure,prior=prior,
                loading_settings={key:getattr(args,key) for key in ('time_col','signal_col','error_col','signal_kind','band_col','band')})
    if mode=='discovery':
        result=scout(t,y,dy,args.min_period,args.max_period,root,max_points=args.scout_max_points)
        args.search_windows=json.dumps(result['frequency_windows'])
        args.search_origin='discovery'
        advice['scout']=result
    else:args.search_origin=mode
    import analyze
    f=analyze.frequency_grid(t,args)
    advice['selected']=dict(source=mode,min_period_days=args.min_period,max_period_days=args.max_period,search_windows=args.search_windows,grid_size=len(f))
    fig,ax=plt.subplots(figsize=(10,4));ax.errorbar(t,y,yerr=dy,fmt='.',ms=4,alpha=.8)
    ax.set(xlabel='Days from input epoch',ylabel=meta['label'],title='Before clipping: no rejection decision has been made yet')
    if meta['signal_kind']=='magnitude':ax.invert_yaxis()
    fig.tight_layout();fig.savefig(root/'sampling.png',dpi=140);plt.close(fig)
    esc=lambda x:html.escape(str(x))
    body=f"<h1>Search setup: {esc(args.object_name)}</h1><p>Mode: {mode}; observations: {len(t)}; baseline: {advice['baseline_days']:.9g} days.</p>"
    body+=f"<p>Explicit envelope: {args.min_period:.9g} to {args.max_period:.9g} days ({args.min_period*1440:.8g} to {args.max_period*1440:.8g} minutes). Detailed frequency count: {len(f):,}.</p>"
    body+='<img src="sampling.png" alt="Observations before clipping">'
    if prior:body+='<p>Prior information: '+esc(prior)+'. This is a check around an approximate period, not a blind discovery.</p>'
    if exposure:body+=f'<p>Exposure: {exposure:g} seconds. Integration can attenuate rapid variations; this tool does not correct exposure integration.</p>'
    else:body+='<p>Exposure unknown. No exposure-based frequency cutoff is imposed.</p>'
    if mode=='discovery':
        body+='<h2>Broad reconnaissance</h2><img src="scout_periodograms.png" alt="Broad scout periodograms"><p>Two harmonic models screen the entire declared envelope. Later methods search only the following windows, including available half/double-frequency companions. Gaps are NOT searched by all methods.</p>'
        body+='<table><tr><th>Minimum period (days)</th><th>Maximum period (days)</th></tr>'
        for lo,hi in result['frequency_windows']:body+=f'<tr><td>{1/hi:.10g}</td><td>{1/lo:.10g}</td></tr>'
        body+='</table><p><a href="scout_candidates.csv">Exact rechecked scout candidates</a> | <a href="scout_alias_diagnostics.csv">Harmonic and window relationships</a></p>'
        body+='<ul>'+''.join('<li>'+esc(n)+'</li>' for n in result['limitations'])+'</ul>'
    body+='<p>The median interval between observations does not impose a hard lower period cutoff. No universal period range or unique correct period is guaranteed. Return to the console to continue.</p>'
    body+='<p>Background: <a href="https://docs.astropy.org/en/stable/timeseries/lombscargle.html">Astropy Lomb-Scargle documentation</a>; <a href="https://doi.org/10.3847/1538-4365/aab766">VanderPlas (2018)</a>.</p>'
    (root/'RANGE_ADVICE.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Search setup</title><style>body{font:17px system-ui;max-width:1100px;margin:30px auto;padding:20px;color:#18304b}img{max-width:100%}table{border-collapse:collapse}td,th{border:1px solid #ccd;padding:8px}</style>'+body+'</html>',encoding='utf-8')
    (root/'range_advice.json').write_text(json.dumps(advice,indent=2),encoding='utf-8')
    _save_results_bundle(root,'search setup only; analysis has not run yet')
    return root,advice


def choose_period_range(argv):
    import analyze
    import numpy as np
    import webbrowser
    args=_wizard_args(argv)
    t,y,dy,excluded,meta=analyze.load_data(args)
    exposure_text=_ask('Exposure duration in SECONDS (blank = unknown)')
    exposure=None
    if exposure_text:
        exposure=float(exposure_text)
        if not np.isfinite(exposure) or exposure<=0:raise ValueError('Exposure must be positive and finite or left blank.')
    print(f'Valid observations: {len(t)}; baseline: {np.ptp(t):.9g} days.')
    print('1. Unknown period: broad LS / H=2 reconnaissance, then all selected methods in candidate windows')
    print('2. Approximately known period: enter minutes, hours or days and a relative half-width')
    print('3. Manual continuous period range')
    print('No short-period cutoff is inferred from sparse cadence. Reconnaissance can miss other signal shapes.')
    while True:
        choice=_ask('Choose search mode 1-3','1')
        prior=None;mode={'1':'discovery','2':'known','3':'manual'}.get(choice)
        if mode is None:print('Choose 1, 2 or 3.');continue
        if choice=='2':
            unit=_ask('Approximate period unit: minutes, hours or days','minutes')
            try:factor=_period_factor(unit)
            except ValueError as exc:print(exc);continue
            period=_positive_number('Approximate period')*factor
            width=_positive_number('Relative half-width in percent (e.g. 2 means +/-2%)','2')
            if width>=100:print('Half-width must be below 100%.');continue
            args.min_period=period*(1-width/100);args.max_period=period*(1+width/100)
            prior=dict(approximate_period_days=period,half_width_percent=width)
        else:
            unit=_ask('Bounds unit: minutes, hours or days','minutes' if choice=='1' else 'days')
            try:factor=_period_factor(unit)
            except ValueError as exc:print(exc);continue
            if choice=='1':print('The example bounds are editable search limits, not inferred properties of this star.')
            args.min_period=_positive_number('Shortest trial period',str((20/1440)/factor) if choice=='1' else None)*factor
            args.max_period=_positive_number('Longest trial period',str((float(np.ptp(t))/2)/factor) if choice=='1' else None)*factor
        if args.min_period>=args.max_period:print('Shortest must be below longest.');continue
        args.search_windows=None
        if mode!='discovery':
            try:analyze.frequency_grid(t,args)
            except ValueError as exc:
                print(str(exc))
                if _ask('Screen this same envelope first and compare candidate windows? y/n','y').lower()=='y':mode='discovery'
                else:continue
        if exposure and args.min_period*86400<2*exposure:print('Warning: shortest period is below twice the exposure; integration can attenuate rapid variations.')
        try:root,advice=create_search_plan(args,t,y,dy,meta,mode,exposure,prior)
        except ValueError as exc:print(str(exc));continue
        break
    for row in advice.get('scout',{}).get('candidates',[]):
        print(f"Scout H={row['harmonics']} candidate {row['rank_within_model']}: {row['period_days']:.10g} d = {row['period_days']*1440:.8g} min")
    print(f'Detailed search: {advice["selected"]["grid_size"]:,} frequencies. Monte Carlo repeats this grid.')
    print('SEARCH SETUP: '+str(root/'RANGE_ADVICE.html'))
    webbrowser.open((root/'RANGE_ADVICE.html').resolve().as_uri())
    result=['--min-period',str(args.min_period),'--max-period',str(args.max_period),'--search-origin',mode,'--range-advice',str(root/'range_advice.json')]
    if args.search_windows:result+=['--search-windows',args.search_windows]
    return result


def choose_monte_carlo(argv):
    import analyze
    print('Monte Carlo perturbs measurements and repeats EACH selected supported method on the selected grid.')
    print('It holds clipping and any data-selected windows fixed; it is not a probability that a period is true.')
    while True:
        choice=_ask('Enable Monte Carlo? y/n','n').lower()
        if choice in ('y','yes','n','no'):break
    if choice in ('n','no'):
        return ['--bootstrap','0','--uncertainty-trials','0','--no-recommend']
    # Reuse the exact load settings; range metadata is an application-level flag.
    clean=list(argv)
    if '--range-advice' in clean:
        i=clean.index('--range-advice');del clean[i:i+2]
    args=_wizard_args(clean)
    _,_,dy,_,_=analyze.load_data(args)
    extra=[]
    if dy is None:
        print('No measurement errors. An adjacent-difference MAD estimate can include variability and is not an instrumental uncertainty.')
        if _ask('Explicitly use that empirical noise estimate? y/n','n').lower()!='y':
            print('Measurement Monte Carlo disabled: no error model selected.')
            return ['--bootstrap','0','--uncertainty-trials','0','--no-recommend']
        extra=['--noise-estimate','difference']
    while True:
        count=_positive_number('Number of repetitions (10 = quick check; 100 or more for exploration)','100')
        if count.is_integer():break
        print('Enter a whole number.')
    count=int(count)
    print('Full mode also uses residual-block simulations for its separate joint model and injection/recovery for method comparison.')
    return extra+['--bootstrap',str(count),'--uncertainty-trials',str(count)]


def column_suggestions(df, kind='auto', signal=None):
    from analyze import normalized
    def matches(names):return [c for c in df.columns if normalized(c) in names]
    def unique(values):return values[0] if len(values)==1 else None
    magnitudes=matches({'mag','magnitude','vmag','gmag','rmag'})
    fluxes=matches({'flux'})
    ratios=matches({'vr'})
    generic=matches({'signal','y','brightness'})
    if signal is None:
        if kind=='magnitude':signal=unique(magnitudes)
        elif kind=='flux':signal=unique(fluxes)
        elif kind=='vr':signal=unique(ratios)
        else:
            # Display this preference explicitly; users may override it.
            if len(magnitudes)==1 and not ratios:signal=magnitudes[0]
            elif not magnitudes and not ratios and len(fluxes)==1:signal=fluxes[0]
            elif not magnitudes and not fluxes and len(ratios)==1:signal=ratios[0]
            elif not magnitudes and not fluxes and not ratios:signal=unique(generic)
    inferred='magnitude' if signal in magnitudes else 'flux' if signal in fluxes else 'vr' if signal in ratios else 'auto'
    specific=matches({normalized(signal)+suffix for suffix in ('err','error','sigma')}|{'e'+normalized(signal)}) if signal else []
    errors=specific or matches({'dy','yerr','error','err','sigma'})
    return dict(time=unique(matches({'jd','hjd','bjd','mjd','time'})),signal=signal,error=unique(errors),kind=inferred)


def interactive_arguments():
    print('STAR PERIOD TOOL: UPLOAD_DATA_HERE -> validation -> residual clipping -> analysis -> RESULTS')
    path=select_input(interactive=True)
    _activate_modules()
    from analyze import read_observation_table
    df=read_observation_table(path)
    hints=column_suggestions(df)
    print('Available columns: '+', '.join(map(str,df.columns)))
    print('Press Enter to accept each displayed suggestion; type a column name to override it.')
    print('When both magnitude and flux are available, one unambiguous magnitude column is suggested first.')
    name=_ask('Star/object name',path.stem)
    kind=_ask('Signal type: magnitude, flux, vr, other or auto',hints['kind'])
    unit=_ask('Input time unit: days, hours, minutes or seconds (verify for generic time columns)','days')
    argv=['--input',str(path),'--object-name',name,'--signal-kind',kind,
          '--time-unit',unit,'--output-dir',str(APP_ROOT/'RESULTS')]
    hints=column_suggestions(df,kind)
    tc=_ask('Time column',hints['time'])
    if tc:argv+=['--time-col',tc]
    yc=_ask('Signal column',hints['signal'])
    if yc:argv+=['--signal-col',yc]
    hints=column_suggestions(df,kind,yc)
    ec=_ask('Error column (blank if no suggestion = detect if available)',hints['error'])
    if ec:argv+=['--error-col',ec]
    threshold=float(_ask('Residual clipping threshold: 3 is default; 0 disables clipping','3'))
    if threshold==0:argv.append('--no-clip')
    else:argv += ['--clip-sigma',str(threshold)]
    print('1. Full comparison + conditional recommendation + refined model')
    print('2. Compare four base methods')
    print('3. Lomb-Scargle only   4. Fourier only   5. PDM only   6. WWZ only')
    print('7. Preprocessing only (save cleaned data and stop)')
    mode=_ask('Choose analysis mode (1-7)','1')
    if mode not in tuple('1234567'):raise ValueError('Choose a number from 1 to 7.')
    if mode!='1':argv.append('--basic')
    if mode in '3456':argv += ['--methods',{'3':'ls','4':'fourier','5':'pdm','6':'wwz'}[mode]]
    if mode=='7':argv.append('--preprocess-only')
    else:argv.append('--step-by-step')
    argv.append('--open-report')
    _activate_modules()
    argv += choose_period_range(argv)
    if mode!='7':argv += choose_monte_carlo(argv)
    print('Clipping uses a preliminary period search. Full validation can take minutes or longer.')
    return argv


def _export_preprocessing(out,payload):
    import shutil
    import pandas as pd
    import numpy as np
    from matplotlib import pyplot as plt
    data=payload['data'];args=payload['parameters']
    source=Path(args['input'])
    shutil.copyfile(source,out/('source_input'+source.suffix))
    if (out/'clipping_audit.csv').is_file():
        audit=pd.read_csv(out/'clipping_audit.csv')
        keep=audit['retained'].to_numpy(dtype=bool)
    else:
        audit=pd.read_csv(out/'used_data.csv')
        keep=np.ones(len(audit),dtype=bool)
    factor={'days':1.,'hours':24.,'minutes':1440.,'seconds':86400.}[args['time_unit']]
    table=pd.DataFrame({'time':audit.time_days_from_epoch*factor+data['epoch_input_units'],
                        'signal':audit.signal,'Signal Label':data['label']})
    if 'error' in audit and audit.error.notna().any():table['error']=audit.error
    table.to_csv(out/'valid_data_before_clipping.csv',index=False)
    table.loc[keep].to_csv(out/'clean_data.csv',index=False)
    table.loc[~keep].to_csv(out/'outliers.csv',index=False)
    fig,axes=plt.subplots(2,1,figsize=(11,7),sharex=True)
    axes[0].scatter(audit.time_days_from_epoch,audit.signal,s=14,color='steelblue',label=f'Before clipping: {len(table)}')
    axes[0].set_title('Original valid observations (before clipping)')
    axes[1].scatter(audit.time_days_from_epoch[keep],audit.signal[keep],s=16,color='steelblue',label=f'Retained for base methods: {keep.sum()}')
    axes[1].scatter(audit.time_days_from_epoch[~keep],audit.signal[~keep],s=55,color='red',edgecolors='darkred',linewidths=.8,zorder=5,label=f'Excluded by clipping: {(~keep).sum()}')
    axes[1].set_title('After residual clipping: red points are NOT used by the base methods')
    if keep.all():axes[1].text(.02,.95,'No points excluded' if args['clip_sigma'] is not None else 'Clipping disabled; all valid points retained',transform=axes[1].transAxes,va='top',bbox=dict(facecolor='white',alpha=.8))
    for ax in axes:
        ax.set_ylabel(data['label']);ax.legend(loc='lower right');ax.grid(alpha=.2)
        if data['signal_kind']=='magnitude':ax.invert_yaxis()
    axes[1].set_xlabel('Days from input epoch')
    fig.tight_layout();fig.savefig(out/'sigma_clipping_result.png',dpi=150);plt.close(fig)
    # The earlier search page is explicitly pre-clipping; append the real rejection result when available.
    setup=out/'RANGE_ADVICE.html'
    if setup.exists():
        html=setup.read_text(encoding='utf-8')
        if 'id="after-clipping"' not in html:
            setup.write_text(html.replace('</html>','<section id="after-clipping"><h2>Clipping completed</h2><img src="sigma_clipping_result.png" alt="Before and after clipping; excluded points in red"></section></html>'),encoding='utf-8')
    record=dict(valid_before=len(table),retained=int(keep.sum()),flagged=int((~keep).sum()),
                sigma_threshold=args['clip_sigma'],exported_time_unit=args['time_unit'],
                source_sha256=payload['input_sha256'],
                base_methods_scope='retained_after_optional_clipping',
                recommendation_and_joint_scope='original_valid_before_optional_clipping')
    (out/'preprocessing.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    lines=['# Preprocessing audit','',
           f"Valid before clipping: {len(table)}; retained: {keep.sum()}; flagged: {(~keep).sum()}.",
           f"Residual sigma threshold: {args['clip_sigma']}; null means disabled.",
           f"Exported time unit: {args['time_unit']}. Exported time restores the original input epoch.",
           'The source_input snapshot is unchanged. Invalid rows are in excluded_rows.csv.',
           'Flagged observations are candidates for review, not proven bad measurements.',
           'Base methods use retained data; recommendation and joint validation use original valid data.',
           'clean_data.csv and outliers.csv use time/signal and optional error, with a preserved Signal Label.',
           'Reuse the original source for V/R component-error propagation; reduced exports omit component columns.']
    (out/'PREPROCESSING.md').write_text('\n'.join(lines),encoding='utf-8')
    return record


def _write_overview(out, payload):
    data=payload['data']
    lines=['# Star period analysis - main result','',
           f"Object: {payload['parameters']['object_name']}",
           f"Signal: {data['label']} ({data['signal_kind']}); valid observations: {data['valid_rows']}",
           '', '## Base-method candidates','',
           '| Method | Candidate period (days) | Status |','|---|---:|---|']
    for row in payload['results']:
        period=row.get('period_days')
        lines.append(f"| {row['method']} | {period if period is not None else '-'} | {row['status']} |")
    rec=payload.get('recommendation')
    if rec:
        decision=rec['decision']
        lines += ['', '## Conditional comparison', '',
                  f"Decision: {decision['status']}",
                  f"Recommended base method: {decision['method'] or 'no unique method selected'}",
                  'See [recommendation.md](recommendation.md) for comparability, eligibility and failed checks.']
    joint=payload.get('advanced')
    if joint:
        lines += ['', '## Separate refined harmonic model', '',
                  f"Validation status: {joint['status']}",
                  f"Selected harmonics: {joint['selected_harmonics']}",
                  '| Component | Candidate period (days) | Recovery fraction | Conditional p16-p84 (days) |',
                  '|---|---:|---:|---|']
        for row in joint['modes']:
            lines.append(f"| {row['mode']} | {row['period_days']:.10g} | {row['recovery_fraction']} | {row.get('conditional_p16_days','-')} - {row.get('conditional_p84_days','-')} |")
        lines += ['', 'See [advanced.md](advanced.md) and [joint_fit.png](joint_fit.png). This is a separate model family, not a forced winner among the base methods.']
    lines += ['', '## Interpretation', '',
              'No unique physical period is guaranteed. Compare aliases and harmonics, inspect phase curves, and retain negative validation outcomes. Conditional intervals are not calibrated confidence guarantees.',
              'For V/R, periods describe spectral intensity-ratio variability, not automatically stellar pulsation.',
              '', '## Files to open', '',
              '- [report.md](report.md): detailed comparison and error provenance.',
              '- [phase_curves.png](phase_curves.png): candidate phase curves.',
              '- [periodograms.png](periodograms.png): peaks and observing window.',
              '- [run.json](run.json): settings, input checksum and full numerical results.',
              '- [error_audit.csv](error_audit.csv): measurement errors and empirical noise kept separate.']
    lines += ['', '## Final candidates', '', 'See FINAL_PERIODS.csv for leading and alternative periods in days and minutes; FINAL_RESULT.json records the decision. No unique winner is forced.', '', 'Measurement Monte Carlo repetitions per selected supported method: '+str(payload['parameters']['bootstrap'])+'. See MONTE_CARLO.md and monte_carlo_summary.csv when enabled.']
    for row in payload.get('final_result',{}).get('candidates',[]):
        if row['rank']==1:lines.append(f"- {row['method']}: {row['period_days']:.10g} days = {row['period_minutes']:.8g} minutes ({row['scope']}).")
    (out/'START_RESULT.md').write_text('\n'.join(lines),encoding='utf-8')


def _save_results_bundle(out, stage):
    """Archive one run, including relative HTML assets; never include previous ZIPs."""
    import html
    import re
    import zipfile
    out=Path(out)
    archive=out/'SAVE_RESULTS.zip'
    marker=r'<section id="save-results-panel"[^>]*>.*?</section>'
    footer=('<section id="save-results-panel" style="margin:40px 0;padding:24px;border:1px solid #ccd;border-radius:12px;background:#fff">'
            '<h2>Save your results</h2><p>Saved stage: '+html.escape(stage)+'. Files are already stored on this computer.</p>'
            '<a href="SAVE_RESULTS.zip" download="'+html.escape(out.name)+'-results.zip" style="display:inline-block;padding:12px 20px;background:#185abc;color:white;border-radius:8px;text-decoration:none">Save all available results (ZIP)</a> '
            '<button type="button" onclick="window.print()" style="padding:12px;margin-left:8px;cursor:pointer">Print / Save PDF</button>'
            '<p>The ZIP contains the reports, figures, tables, settings and any saved source-data snapshot available at this stage. Extract the whole ZIP before opening an HTML report.</p>'
            '<p>PDF printing saves this page only. The download destination depends on your browser settings; you can also right-click the ZIP link and save it.</p>'
            '<p>Local results folder: <code>'+html.escape(str(out.resolve()))+'</code></p></section>')
    for page in out.glob('*.html'):
        text=page.read_text(encoding='utf-8')
        text=re.sub(marker,'',text,flags=re.S)
        text=text.replace('</html>',footer+'</html>') if '</html>' in text else text+footer
        page.write_text(text,encoding='utf-8')
    files=sorted(p for p in out.rglob('*') if p.is_file() and p.suffix.lower() not in ('.zip','.tmp') and not p.is_symlink())
    record=dict(stage=stage,files=[p.relative_to(out).as_posix() for p in files if p.name!='SAVE_BUNDLE.json'],note='A stage snapshot. Exported HTML uses relative assets; ZIP download controls are replaced in the exported copy to avoid recursive archives.')
    (out/'SAVE_BUNDLE.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    files=sorted(set(files+[out/'SAVE_BUNDLE.json']))
    temp=out/'SAVE_RESULTS.zip.tmp'
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        for path in files:
            name=out.name+'/'+path.relative_to(out).as_posix()
            if path.suffix.lower()=='.html':
                text=path.read_text(encoding='utf-8')
                replacement='<section id="exported-copy"><h2>Saved report copy</h2><p>This report and its figures and tables are included in the extracted folder. Keep them together when copying or sharing.</p><button type="button" onclick="window.print()">Print / Save PDF</button></section>'
                z.writestr(name,re.sub(marker,replacement,text,flags=re.S))
            else:z.write(path,name)
    temp.replace(archive)
    return archive


def _visual_report(out, payload, final=False):
    import html
    esc=lambda value: html.escape(str(value))
    info=json.loads((out/'preprocessing.json').read_text(encoding='utf-8'))
    body=f"<h1>{esc(payload['parameters']['object_name'])}: period analysis</h1>"
    if final:
        body+='<h2>Final period candidates</h2><p>Leading candidates from each method, not automatically confirmed physical periods. Alternatives are in <a href="FINAL_PERIODS.csv">FINAL_PERIODS.csv</a>.</p><table><tr><th>Method</th><th>Days</th><th>Minutes</th><th>Scope</th></tr>'
        for row in payload.get('final_result',{}).get('candidates',[]):
            if row['rank']==1 or row['method']=='refined_joint_model':body+=f"<tr><td>{esc(row['method'])}</td><td>{row['period_days']:.10g}</td><td>{row['period_minutes']:.8g}</td><td>{esc(row['scope'])}</td></tr>"
        body+='</table><p>Decision: '+esc(payload.get('final_result',{}).get('status'))+'</p>'
        if payload['parameters'].get('search_origin')=='discovery':body+='<p><strong>Data-selected windows:</strong> the broad screen and later analysis use the same observations. Comparisons and uncertainty are conditional on the retained windows. Other periods may have been missed.</p>'
    body+=f"<h2>1. Preprocessing</h2><p>Valid: {info['valid_before']} | Retained: {info['retained']} | Flagged: {info['flagged']}</p>"
    body+='<p>One residual-clipping pass after a preliminary period search. Flagged points require review.</p>'
    body+='<img src="sigma_clipping_result.png" alt="Retained and flagged observations">'
    body+='<p><a href="clean_data.csv">Clean data</a> | <a href="outliers.csv">Flagged points</a> | <a href="PREPROCESSING.md">Preprocessing details</a></p>'
    if final:
        body+='<h2>2. Selected methods: retained observations</h2><table><tr><th>Method</th><th>Candidate period (days)</th><th>Status</th></tr>'
        for row in payload['results']:
            body+=f"<tr><td>{esc(row['method'])}</td><td>{esc(row.get('period_days','-'))}</td><td>{esc(row['status'])}</td></tr>"
        body+='</table>'
        if (out/'phase_curves.png').exists():body+='<img src="phase_curves.png" alt="Phase curves">'
        for row in payload['results']:
            method=row['method']
            body+=f'<h3>{esc(method)} periodogram</h3><img src="{method}_periodogram.png" alt="Periodogram with leading period">'
            if (out/(method+'_peak_details.png')).exists():body+=f'<img src="{method}_peak_details.png" alt="Leading peaks in minutes">'
            if payload['parameters']['bootstrap']:
                body+=f'<p>Monte Carlo: {esc(row.get("monte_carlo_status"))}; repetitions: {payload["parameters"]["bootstrap"]}; same-peak fraction of all trials: {esc(row.get("same_peak_fraction","not available"))}.</p><img src="{method}_monte_carlo.png" alt="Monte Carlo period distribution">'
        body+='<img src="sampling_window.png" alt="Observing window">'
        if payload['parameters']['bootstrap']:body+='<p><a href="MONTE_CARLO.md">Monte Carlo assumptions</a> | <a href="monte_carlo_summary.csv">Numerical Monte Carlo summary</a>. Intervals are conditional and not calibrated confidence guarantees.</p>'
        else:body+='<p>Measurement Monte Carlo disabled by the selected settings.</p>'
        if payload.get('recommendation'):
            d=payload['recommendation']['decision']
            body+=f"<h2>3. Validation on original valid observations</h2><p>Decision: {esc(d['status'])}. Preferred method: {esc(d['method'] or 'no unique choice')}.</p>"
            body+='<p><a href="recommendation.md">Validation details</a>. This checks the original data, before clipping; it does not rank the cleaned-data estimates.</p>'
        if payload.get('advanced'):
            body+='<h2>Refined harmonic model on original observations</h2>'
            for row in payload['advanced']['modes']:
                body+=f"<p>Component {esc(row['mode'])}: {esc(row['period_days'])} days</p>"
            body+='<p><a href="advanced.md">Model validation and conditional uncertainty</a></p><img src="joint_fit.png" alt="Joint fit">'
        body+='<p>Candidate periods are not automatically confirmed physical periods. A unique best method may not be established.</p><a href="START_RESULT.md">Detailed overview</a>'
    else:
        body+='<h2>2. Analysis pending</h2><p>Return to the console to continue or stop. For a preprocessing-only run, this is the final result.</p>'
    if (out/'RANGE_ADVICE.html').exists():body+='<p><a href="RANGE_ADVICE.html">Search-range proposals</a> | <a href="range_advice.json">Saved range choice</a></p>'
    name='RESULT.html' if final else 'PREPROCESSING.html'
    (out/name).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Star period analysis</title><style>body{font:17px system-ui;max-width:1050px;margin:40px auto;padding:0 24px;color:#18304b;background:#f6f8fb}img{max-width:100%;background:white}table{border-collapse:collapse;background:white;width:100%}td,th{padding:12px;border:1px solid #cbd5e1;text-align:left}h2{margin-top:32px}a{color:#1262ad}</style>'+body+'</html>',encoding='utf-8')
    return out/name


def _prune_previous_results(current, protected_paths=()):
    """Delete only older recognized completed runs, after a verified new ZIP exists."""
    import re
    import shutil
    import zipfile
    current=Path(current).resolve()
    root=current.parent
    if not all((current/name).is_file() for name in ('run.json','RESULT.html','SAVE_RESULTS.zip')):
        raise ValueError('Cleanup requires a completed report and ZIP.')
    with zipfile.ZipFile(current/'SAVE_RESULTS.zip') as z:
        if z.testzip() is not None:raise ValueError('Result ZIP failed verification; old results preserved.')
        if current.name+'/run.json' not in z.namelist():raise ValueError('Result ZIP is incomplete; old results preserved.')
    stamp=current.name.removeprefix('run_') if hasattr(str,'removeprefix') else current.name[4:]
    protected=[Path(p).resolve() for p in protected_paths if p]
    removed=[];skipped=[]
    for entry in root.iterdir():
        match=re.fullmatch(r'(run|search)_(\d{8}T\d{6}_\d{6}Z)',entry.name)
        if not match or match[2]>=stamp or not entry.is_dir():continue
        resolved=entry.resolve()
        # Do not traverse symlinks/junctions or leave the selected output root.
        if entry.is_symlink() or resolved!=entry.absolute() or resolved.parent!=root or resolved==current:continue
        if any(p==resolved or resolved in p.parents for p in protected):continue
        if match[1]=='run':
            recognized=(entry/'run.json').is_file() and (entry/'START_RESULT.md').is_file()
        else:recognized=(entry/'range_advice.json').is_file() and (entry/'RANGE_ADVICE.html').is_file()
        if not recognized:continue
        try:
            shutil.rmtree(resolved)
            removed.append(entry.name)
        except OSError as exc:
            skipped.append(dict(folder=entry.name,error=str(exc)))
    record=dict(removed=removed,not_removed=skipped,policy='Keep newest completed run; preserve unknown folders, newer runs, unfinished runs and active input paths.')
    (current/'cleanup.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(f'Results cleanup: removed {len(removed)} previous result/search folders; current report retained.',flush=True)
    for row in skipped:print('Could not remove '+row['folder']+': '+row['error'],flush=True)
    return record


def run_combined(argv):
    """Run every requested method plus conditional comparison and joint refinement."""
    _activate_modules()
    import analyze
    argv=list(argv)
    keep_history='--keep-history' in argv
    argv=[arg for arg in argv if arg!='--keep-history']
    discover='--discover' in argv
    no_recommend='--no-recommend' in argv
    argv=[v for v in argv if v not in ('--discover','--no-recommend')]
    range_record=None
    if '--range-advice' in argv:
        i=argv.index('--range-advice')
        if i+1>=len(argv):raise ValueError('--range-advice requires a JSON path.')
        range_record=Path(argv[i+1]);del argv[i:i+2]
    step='--step-by-step' in argv
    only='--preprocess-only' in argv
    open_report='--open-report' in argv
    argv=[x for x in argv if x not in ('--step-by-step','--preprocess-only','--open-report')]
    if only and '--basic' not in argv:argv.append('--basic')
    def supplied(flag):return any(arg==flag or arg.startswith(flag+'=') for arg in argv)
    if not supplied('--input') and not any(arg in ('--help','-h') for arg in argv):
        argv += ['--input',str(select_input())]
    if not supplied('--output-dir'):argv += ['--output-dir',str(APP_ROOT/'RESULTS')]
    no_clip='--no-clip' in argv
    if no_clip and supplied('--clip-sigma'):raise ValueError('Choose --no-clip or --clip-sigma, not both.')
    argv=[arg for arg in argv if arg!='--no-clip']
    if not no_clip and not supplied('--clip-sigma'):argv += ['--clip-sigma','3']
    basic='--basic' in argv
    argv=[arg for arg in argv if arg!='--basic']
    if not basic:
        for flag in (['--advanced','--auto-harmonics']+([] if no_recommend else ['--recommend'])):
            if flag not in argv:argv.append(flag)
        for flag,value in [('--uncertainty-mode','block'),('--uncertainty-trials','100'),('--max-modes','1')]:
            if not any(arg==flag or arg.startswith(flag+'=') for arg in argv):
                argv += [flag,value]
    args=analyze.parser().parse_args(argv)
    if discover:
        if range_record:raise ValueError('Choose --discover or an existing --range-advice record.')
        t,y,dy,excluded,meta=analyze.load_data(args)
        root,advice=create_search_plan(args,t,y,dy,meta,'discovery')
        range_record=root/'range_advice.json'
    if range_record:
        advice=json.loads(range_record.read_text(encoding='utf-8'))
        selected=advice.get('selected',{})
        if advice['input_sha256']!=hashlib.sha256(Path(args.input).read_bytes()).hexdigest():
            raise ValueError('Input changed since range advice; regenerate the advice.')
        if selected.get('search_windows')!=args.search_windows:raise ValueError('Selected windows differ from the saved search setup.')
        if advice.get('loading_settings') and any(getattr(args,k)!=v for k,v in advice['loading_settings'].items()):raise ValueError('Loading settings differ from the saved search setup.')
        if selected.get('min_period_days')!=args.min_period or selected.get('max_period_days')!=args.max_period or advice['input_time_unit']!=args.time_unit:
            raise ValueError('Selected bounds or time units differ from the saved range advice.')
    def preview(out, payload):
        import webbrowser
        if range_record:
            import shutil
            shutil.copyfile(range_record,out/'range_advice.json')
            for name in ('RANGE_ADVICE.html','sampling.png','scout_periodograms.png','scout_candidates.csv','scout_alias_diagnostics.csv','scout_plot_envelope.csv'):
                src=range_record.parent/name
                if src.exists():shutil.copyfile(src,out/name)
        info=_export_preprocessing(out,payload)
        page=_visual_report(out,payload)
        _save_results_bundle(out,'preprocessing; period analysis not yet completed')
        print(f"Stage 1 complete: {info['retained']} retained, {info['flagged']} flagged.",flush=True)
        print('OPEN PREPROCESSING: '+str(page.resolve()),flush=True)
        if open_report:webbrowser.open(page.resolve().as_uri())
        if only:return False
        if step:
            answer=_ask('Review the graph. Continue to analysis? y/n','y').lower()
            if answer not in ('y','yes','n','no'):raise ValueError('Enter y or n; preprocessing results have been saved.')
            if answer in ('n','no'):return False
        print('Stage 2: analyzing the retained data...',flush=True)
        return True
    out=analyze.run(args,preprocessing_callback=preview)
    if not (out/'run.json').exists():
        _save_results_bundle(out,'stopped after preprocessing')
        print('Stopped after preprocessing. Results saved: '+str(out.resolve()))
        return out
    payload=json.loads((out/'run.json').read_text(encoding='utf-8'))
    preprocessing=_export_preprocessing(out,payload)
    from presentation import final_candidates
    payload['final_result']=final_candidates(out,payload)
    _write_overview(out,payload)
    with (out/'START_RESULT.md').open('a',encoding='utf-8') as report:
        report.write('\n\n## Preprocessing and analysis scope\n\n')
        report.write(f"Valid input: {preprocessing['valid_before']}; retained: {preprocessing['retained']}; flagged: {preprocessing['flagged']}.\n\n")
        report.write('Base-method periods use retained observations. Recommendation and the refined joint model use original valid observations before clipping.\n\nSee [PREPROCESSING.md](PREPROCESSING.md) and [sigma_clipping_result.png](sigma_clipping_result.png).\n')
    manifest={'application':'MainC.py',
              'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'embedded_module_sha256':{name:hashlib.sha256(code.encode('utf-8')).hexdigest() for name,code in EMBEDDED_SOURCES.items()},
              'mode':'basic' if basic else 'combined'}
    (out/'tool_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    page=_visual_report(out,payload,final=True)
    archive=_save_results_bundle(out,'completed analysis')
    if not keep_history:
        _prune_previous_results(out,[args.input,args.validation_input])
        archive=_save_results_bundle(out,'completed analysis')
    print('SAVE ALL RESULTS: '+str(archive.resolve()))
    if open_report:
        import webbrowser
        webbrowser.open(page.resolve().as_uri())
    print('VISUAL RESULT: '+str(page.resolve()))
    print('\nOPEN THIS RESULT FIRST: '+str((out/'START_RESULT.md').resolve()))
    return out


def self_test():
    """A small known-period check, not scientific validation across stellar types."""
    import tempfile
    import numpy as np
    import pandas as pd
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);rng=np.random.default_rng(42)
        t=np.sort(rng.uniform(0,10,160));period=.7
        y=np.sin(2*np.pi*t/period)+rng.normal(0,.04,len(t))
        path=root/'synthetic.csv'
        pd.DataFrame({'time':t,'flux':y,'error':.04}).to_csv(path,index=False)
        out=run_combined(['--basic','--input',str(path),'--min-period','.5',
                         '--max-period','1','--harmonics','1','--wwz-centers','8',
                         '--output-dir',str(root/'results')])
        payload=json.loads((out/'run.json').read_text(encoding='utf-8'))
        for row in payload['results']:
            if row.get('period_days') is None or abs(row['period_days']/period-1)>.03:
                raise RuntimeError('Known-period check failed for '+row['method'])
        print('SELF-TEST PASSED: all four methods recover 0.7 days within 3%. Temporary outputs are removed.')


def main():
    if sys.argv[1:]==['--manual']:
        print(__doc__)
        return 0
    try:
        if sys.argv[1:]==['--self-test']:
            self_test()
        else:
            argv=sys.argv[1:] or interactive_arguments()
            run_combined(argv)
    except ModuleNotFoundError as exc:
        print('Missing library: '+str(exc)+'. See the installation command at the top of this file or run --manual.',file=sys.stderr)
        return 2
    except (ValueError,OSError,RuntimeError,EOFError) as exc:
        print('Analysis error: '+str(exc),file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('\nAnalysis interrupted by the user.',file=sys.stderr)
        return 130
    return 0


if __name__=='__main__':
    raise SystemExit(main())
