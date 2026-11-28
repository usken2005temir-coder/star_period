# v2 validation record

Date: 2026-11-23. This is a limited engineering and recovery check, not a population accuracy or calibrated uncertainty study.

## Automated checks

45 existing numerical/input regression checks passed. Fifteen added workflow checks passed, including explicit no-supported-period handling. New tests are supplied in TESTS/test_workflow.py.

## Sparse-timing injections

Times and measurement-error scales were taken from the supplied AP17210606 (2).csv (413 rows, baseline approximately 2226.98 days). Brightness values were replaced with synthetic two-harmonic signals plus Gaussian noise (amplitudes 0.25 and 0.08; seeds 240, 241, 242). The scout used a fixed 0.02-to-10-day envelope, 1,111,265 frequencies and up to three candidates per harmonic model.

| Injected period, days | Recovered scout candidate, days | Difference, seconds | Within 1/T in frequency |
|---:|---:|---:|---|
| 0.0618055555556 | 0.0618055461808 | -0.0008099804 | True |
| 0.0951388888889 | 0.0951388703513 | -0.001601652 | True |
| 0.73 | 0.7299998871 | -0.009754534 | True |

All three injected frequencies remained within proposed windows. These few successes do not establish recovery probability, coverage or robustness across amplitudes and stellar classes.

## Actual supplied measurements

One reconnaissance-plus-base-method run used the original 413 measurements, HJD/mag/mag_err, a 0.02-to-10-day envelope, 3-sigma residual clipping, two Fourier harmonics and eight WWZ centers. It retained 405 points and flagged 8. Flagging does not prove that measurements are defective; calibration differences and waveform mismatch need review. Camera offsets were not modeled.

Leading retained-data candidates:

- Lomb-Scargle: approximately 0.06103834762 days (87.895221 minutes).
- Fourier: approximately 0.06103836434 days (87.895245 minutes).
- PDM: approximately 0.06103831419 days (87.895172 minutes).
- WWZ: insufficient local support in the selected windows.

This is an exploratory software check of a user-labelled object, not independent verification of the catalogue identity or publication-grade period precision. Digits reflect grid candidates, not demonstrated uncertainty. The analysis was not forced to return 89 minutes. No unique validated winner is claimed.

## End-to-end checks

A sparse synthetic 89-minute signal with one injected outlier exercised clipping, all four methods, three measurement perturbations per supported method, reports and unavailable-WWZ handling.

A separate dense synthetic 0.7-day signal exercised all four supported methods, clipping, three measurement perturbations, automatic harmonic selection up to H=2, three joint-model simulations and three recommendation injections. All base candidates were approximately 0.700133 days; the separate original-data joint model was approximately 0.699158 days. The deliberately injected outlier remained in that original-data check. The recommendation was inconclusive, as expected with only three injections.

Three simulations are a functional check ONLY; no calibrated confidence limits or scientific recovery fractions are established. Broad screening and clipping are not repeated in the measurement Monte Carlo.

## Scientific limits

Fixed, data-selected windows make later comparisons and uncertainty conditional. LS/H=2 screening is not exhaustive across model families. Some real periodicities can be missed. For a continuous independently specified range, use manual/known mode. A correct tool must preserve inconclusive and unsupported results rather than manufacture a best period.
