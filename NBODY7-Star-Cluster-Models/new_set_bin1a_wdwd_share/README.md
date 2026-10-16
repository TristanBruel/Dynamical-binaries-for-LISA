# Double white-dwarf (WD–WD) binaries from star-cluster simulations

This folder contains **90 HDF5 files**, one per simulated star cluster, holding every
**double white-dwarf (WD–WD) binary** found in that model — both while bound inside the
cluster and at the moment it was ejected.

Each file is self-describing: all of the information below is also stored as HDF5
attributes (file-level and per-dataset `units` / `description`).

---

## 1. Provenance

The binaries were extracted from `NBODY6/7` (`updated-nbody7`) cluster evolution runs:

- **In-cluster binaries** come from the `fort.82` snapshot dump (source format:
  `Block/hrplot.f`). One snapshot is written every plotting interval.
- **Escaped binaries** come from the `BINARY ESCAPE` lines of the run stdout (`run.out`;
  source format: `Block/escape.f`).

A **WD–WD binary** is one whose *both* components are white dwarfs, i.e. stellar type
`kw1` ∈ {10, 11, 12} **and** `kw2` ∈ {10, 11, 12}, where
`10 = He WD`, `11 = CO WD`, `12 = ONe WD`.

## 2. File naming

```
M{mass}k_rh{rh}_{runid}_Z{Z}_wdwd_binaries.h5
```

e.g. `M75k_rh2_1501_Z0002_wdwd_binaries.h5`:

| token   | meaning                                          | example       |
|---------|--------------------------------------------------|---------------|
| `M75k`  | initial cluster mass = 75 × 10³ M☉               | 75000 M☉      |
| `rh2`   | initial half-mass radius = 2 (pc)                | 2 pc          |
| `1501`  | run / realization ID (random seed)               | 1501          |
| `Z0002` | metallicity, digits after “0.” → `0.0002`        | Z = 0.0002    |

The full model path (with any further parameters) is in the file attribute
`source_combo_dir`.

## 3. HDF5 layout

Each file has a single group **`wdwd`** containing one 1-D dataset per column, all of
equal length, **sorted by time**. Think of it as one flat table:

> **one row = one binary at one instant.**

A binary is identified by its **unordered component-ID pair** `(name1, name2)`; these IDs
are persistent across the whole run, so you can follow a binary over time by selecting
all rows with the same pair. *(Note: the stored order of `name1`/`name2` may swap between
rows — always match on the unordered pair, e.g. `tuple(sorted((name1, name2)))`.)*

### The key column: `record_type`

| `record_type` | source                  | meaning                                                                 |
|:-------------:|-------------------------|-------------------------------------------------------------------------|
| `0`           | `fort.82` snapshot      | binary **bound in the cluster** at time `time`; full state recorded.    |
| `1`           | `run.out` BINARY ESCAPE | binary **at the moment of ejection**; `time` = escape time.             |

A `record_type = 1` row is the binary's *true* state at ejection, which can differ from
its last in-cluster snapshot (e.g. the in-cluster period is capped — see §6). For an
escape row, only the orbital/stellar-type quantities are available; `ri`, `zl*`, `r*`,
`te*` are `NaN`, and `semi` is derived from the recorded period and masses via Kepler's
third law.

- A `record_type = 1` row **sharing its pair** with `record_type = 0` rows → the binary
  was tracked in-cluster *and* later escaped (its history is in this file).
- A `record_type = 1` row with **no matching** `record_type = 0` rows → it became WD–WD
  and escaped between snapshots, so it was never logged in-cluster as WD–WD.

### Columns

| column        | dtype  | units         | meaning                                                          |
|---------------|--------|---------------|------------------------------------------------------------------|
| `record_type` | int8   | –             | 0 = in-cluster snapshot, 1 = escape state (see above)            |
| `time`        | f8     | Myr           | physical time of the snapshot (or escape time for `record_type=1`)|
| `name1`       | i4     | –             | persistent ID of component 1                                     |
| `name2`       | i4     | –             | persistent ID of component 2                                     |
| `kw1`         | i4     | –             | stellar type of comp 1 (10–12 = He/CO/ONe WD)                    |
| `kw2`         | i4     | –             | stellar type of comp 2 (10–12 = He/CO/ONe WD)                    |
| `kstar_cm`    | i4     | –             | stellar-type flag of the binary centre of mass                   |
| `m1`          | f8     | M☉            | mass of component 1                                              |
| `m2`          | f8     | M☉            | mass of component 2                                              |
| `ecc`         | f8     | –             | orbital eccentricity                                             |
| `pb`          | f8     | log10(day)    | **log10** orbital period                                         |
| `semi`        | f8     | log10(R☉)     | **log10** semi-major axis                                        |
| `ri`          | f8     | R_c           | distance of c.m. from cluster density centre, in **core radii** (`NaN` for escapers) |
| `ri_pc`       | f8     | pc            | the same distance in **parsecs** = `ri` × RC(t) × R* (`NaN` for escapers, see §6) |
| `zl1`, `zl2`  | f8     | log10(L☉)     | **log10** luminosity of comp 1 / 2 (`NaN` for escapers)          |
| `r1`, `r2`    | f8     | log10(R☉)     | **log10** radius of comp 1 / 2 (`NaN` for escapers)              |
| `te1`, `te2`  | f8     | log10(K)      | **log10** effective temperature of comp 1 / 2 (`NaN` for escapers)|
| `escape_time` | f8     | Myr           | time this binary escaped (constant over all its rows); `NaN` = never escaped |
| `v_eject`     | f8     | km/s          | ejection speed `(V/⟨V⟩)·V*` (set on `record_type=1` rows only; `NaN` otherwise) |

**Several columns are base-10 logarithms** (`pb`, `semi`, `zl*`, `r*`, `te*`). Convert to
physical values with `10**x` — e.g. semi-major axis `a[R☉] = 10**semi`, period
`P[day] = 10**pb`.

`escape_time` lets you flag escapers without scanning `record_type`: any row with a finite
`escape_time` belongs to a binary that escaped (the value equals the `time` of its
`record_type = 1` row). `NaN` means the binary merged/disrupted inside the cluster or was
still bound at the end of the run.

## 4. Primordial vs. dynamical pairs

Because component IDs are assigned sequentially at birth, a **primordial** binary (the two
stars were born paired) has consecutive IDs: `abs(name1 - name2) == 1`. Any other pair was
**dynamically** assembled inside the cluster.

## 5. Per-file attributes (metadata)

Open the file's `.attrs` for run-level metadata, including:

| attribute | meaning |
|-----------|---------|
| `source_combo_dir`        | full path of the source simulation directory |
| `source_files`            | `fort.82, fort.821, run.out` |
| `format_reference`        | NBODY source files defining the formats |
| `wd_definition`           | the WD–WD selection rule |
| `n_snapshots`             | number of `fort.82` snapshots scanned |
| `n_wdwd_rows`             | total rows = `n_incluster_rows + n_escape_rows` |
| `n_incluster_rows`        | number of `record_type = 0` rows |
| `n_escape_rows`           | number of `record_type = 1` rows |
| `n_binary_escapes_total`  | all binary escapes in the run (any type) |
| `n_wdwd_escapers`         | WD–WD escapers (= `n_escape_rows`) |
| `n_tracked_escapers`      | escapers that also have in-cluster history here |
| `n_untracked_escapers`    | escapers with no in-cluster WD–WD record |
| `time_first_myr`, `time_last_myr` | snapshot time span of the run |
| `tstar_myr_per_nbody`     | N-body → Myr time unit (T*) used for escape times |
| `vstar_kms_per_nbody`     | N-body → km/s velocity unit (V*) used for `v_eject` |
| `rstar_pc_per_nbody`      | N-body → pc length unit (R*) used for `ri_pc` |
| `n_core_blocks`           | number of core-radius RC(t) entries read for `ri_pc` |

## 6. Notes & caveats

- **In-cluster period is capped.** The snapshot writer (`hrplot.f`) clips the orbital
  period at 99999.9 day, so `pb` saturates at `log10(99999.9) ≈ 5.0` for wide in-cluster
  binaries. The **escape-row** `pb` is *not* capped, so an escaper's `record_type = 1` row
  can show a longer (truer) period than its last in-cluster snapshot.
- **Radial distance:** `ri` is the c.m. distance in units of the cluster core
  radius (as stored in fort.82); `ri_pc` is the same distance in parsecs,
  `ri_pc = ri × RC(t) × R*`, where the core radius `RC(t)` is taken from the
  run's OUTPUT diagnostics at the nearest time (within ~1 N-body time unit, so
  effectively exact) and `R*` is the N-body length unit in pc. Both columns are
  kept so you can use whichever is convenient.
- **Escape rows carry only orbital/type/mass info**; `ri`, `ri_pc`, `zl*`, `r*`, `te*` are `NaN`,
  and their `semi` is Kepler-derived from the recorded period and total mass.
- **Escape-time precision.** `escape_time = (preceding ADJUST time) × T*`, and `T*` is
  printed to 3 significant figures, so absolute escape times carry ~0.1–0.3 % uncertainty
  (an escape can land up to ~1 snapshot before the last in-cluster `time`).
- **Name order can swap** between rows of the same binary; match on the unordered pair.

## 7. Quick start (Python)

```python
import h5py, numpy as np, pandas as pd

with h5py.File("M75k_rh2_1501_Z0002_wdwd_binaries.h5", "r") as f:
    g = f["wdwd"]
    df = pd.DataFrame({k: g[k][:] for k in g.keys()})
    meta = dict(f.attrs)

# in-cluster snapshots vs. escape-state rows
incluster = df[df.record_type == 0]
escapers  = df[df.record_type == 1]

# physical values from the log10 columns
df["a_Rsun"] = 10.0 ** df["semi"]      # semi-major axis [R_sun]
df["P_day"]  = 10.0 ** df["pb"]        # orbital period  [day]

# identify distinct binaries and primordial vs dynamical
pair = np.sort(df[["name1", "name2"]].to_numpy(), axis=1)
df["pair"]       = list(map(tuple, pair))
df["primordial"] = np.abs(df.name1 - df.name2) == 1

# follow one binary's evolution, time-ordered
for key, trk in df[df.record_type == 0].groupby("pair"):
    trk = trk.sort_values("time")
    # trk.time, trk.a_Rsun, trk.ecc, ...
```

---

*Generated by `extract_wdwd.py` / `sweep_wdwd.py`. Questions: sambaran.banerjee@gmail.com*
