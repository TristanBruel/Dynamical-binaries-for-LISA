# Compact-object binaries from star-cluster simulations

This folder contains **90 HDF5 files**, one per simulated star cluster, holding every
**binary with at least one compact object** (neutron star or black hole) found in that
model — both while bound inside the cluster and at the moment it was ejected — plus the
**double-compact GR mergers** (in-cluster and escaped) associated with those binaries.

Each file is self-describing: all of the information below is also stored as HDF5
attributes (file-level and per-dataset `units` / `description`).

This is the compact-object companion to the double-white-dwarf (WD–WD) dataset; the
layout is identical except for the membership rule, the black-hole Teff convention, and
the extra merger record type (2) described below.

---

## 1. Provenance

The binaries were extracted from `NBODY6/7` (`updated-nbody7`) cluster evolution runs:

- **In-cluster binaries** come from the `fort.82` snapshot dump (source format:
  `Block/hrplot.f`). One snapshot is written every plotting interval.
- **Escaped binaries** come from the `BINARY ESCAPE` lines of the run stdout (`run.out`;
  source format: `Block/escape.f`).
- **GR mergers** come from the initial-inspiral-configuration merger summaries produced by
  `match_mrg_spin0` (see the separate `new_set_bin1a_grmrg_share` dataset):
  `orbitd_summary0_in_ext.dat` (in-cluster mergers) and the escaped tail of
  `orbitd_summary0_ext.dat` (escaped mergers).

A **compact-object binary** here is one whose stellar types satisfy
`kw1 ∈ {13, 14}` **or** `kw2 ∈ {13, 14}` (at least one component), where
`13 = neutron star (NS)`, `14 = black hole (BH)`.

## 2. File naming

```
M{mass}k_rh{rh}_{runid}_Z{Z}_compact_binaries.h5
```

e.g. `M75k_rh2_1502_Z005_compact_binaries.h5`:

| token   | meaning                                          | example       |
|---------|--------------------------------------------------|---------------|
| `M75k`  | initial cluster mass = 75 × 10³ M☉               | 75000 M☉      |
| `rh2`   | initial half-mass radius = 2 (pc)                | 2 pc          |
| `1502`  | run / realization ID (random seed)               | 1502          |
| `Z005`  | metallicity, digits after “0.” → `0.005`         | Z = 0.005     |

The full model path is in the file attribute `source_combo_dir`.

## 3. HDF5 layout

Each file has a single group **`compact`** containing one 1-D dataset per column, all of
equal length, **sorted by time**. Think of it as one flat table:

> **one row = one binary at one instant (or one merger).**

A binary is identified by its **unordered component-ID pair** `(name1, name2)`; these IDs
are persistent across the whole run, so you can follow a binary over time by selecting
all rows with the same pair. *(The stored order of `name1`/`name2` may swap between rows —
always match on the unordered pair, e.g. `tuple(sorted((name1, name2)))`.)*

### The key column: `record_type`

| `record_type` | source                       | meaning                                                             |
|:-------------:|------------------------------|---------------------------------------------------------------------|
| `0`           | `fort.82` snapshot           | binary **bound in the cluster** at time `time`; full state recorded. |
| `1`           | `run.out` BINARY ESCAPE      | binary **at the moment of ejection**; `time` = escape time.          |
| `2`           | `orbitd_summary0[_in]_ext`   | a **double-compact GR merger** (in-cluster or escaped) — see §4.     |

For `record_type = 1`, only the orbital/stellar-type quantities are available; `ri`,
`ri_pc`, `zl*`, `r*`, `te*` are `NaN`, and `semi` is Kepler-derived from the recorded
period and masses. A `record_type = 1` row sharing its pair with `record_type = 0` rows
was tracked in-cluster and later escaped; one with no matching `record_type = 0` rows
became compact and escaped between snapshots.

### Black-hole effective temperature

`fort.82` may store a finite `TE` for a black hole (`kw = 14`); it is not a meaningful
surface temperature. **`te1`/`te2` are set to `NaN` for any `kw = 14` component.**
Neutron stars (`kw = 13`) keep whatever Teff is recorded.

### Columns

| column        | dtype  | units         | meaning                                                          |
|---------------|--------|---------------|------------------------------------------------------------------|
| `record_type` | int8   | –             | 0 = in-cluster, 1 = escape, 2 = merger (see above / §4)           |
| `time`        | f8     | Myr           | snapshot time; escape time (`rt=1`); inspiral-config time (`rt=2`)|
| `name1`       | i4     | –             | persistent ID of component 1 (= `id1` for `rt=2`)                |
| `name2`       | i4     | –             | persistent ID of component 2 (= `id2` for `rt=2`)               |
| `kw1`         | i4     | –             | stellar type of comp 1 (13 = NS, 14 = BH)                        |
| `kw2`         | i4     | –             | stellar type of comp 2 (13 = NS, 14 = BH)                        |
| `kstar_cm`    | i4     | –             | stellar-type flag of the binary centre of mass (−1 if N/A)       |
| `m1`          | f8     | M☉            | mass of component 1                                              |
| `m2`          | f8     | M☉            | mass of component 2                                              |
| `ecc`         | f8     | –             | orbital eccentricity (= inspiral-config `e` for `rt=2`)          |
| `pb`          | f8     | log10(day)    | **log10** orbital period (`NaN` for `rt=2`)                      |
| `semi`        | f8     | log10(R☉)     | **log10** semi-major axis (`NaN` for `rt=2`; see `mrg_semi`)     |
| `ri`          | f8     | R_c           | distance of c.m. from density centre, in **core radii** (`rt=0` only) |
| `ri_pc`       | f8     | pc            | the same distance in **parsecs** = `ri`×RC(t)×R* (`rt=0` only)   |
| `zl1`, `zl2`  | f8     | log10(L☉)     | **log10** luminosity of comp 1 / 2 (`rt=0` only)                 |
| `r1`, `r2`    | f8     | log10(R☉)     | **log10** radius of comp 1 / 2 (`rt=0` only)                     |
| `te1`, `te2`  | f8     | log10(K)      | **log10** Teff of comp 1 / 2 (`rt=0` only; **`NaN` for BH, kw=14**)|
| `escape_time` | f8     | Myr           | binary's ejection time — on its `rt=0`/`rt=1` rows and its **escaped-merger** `rt=2` row; in-cluster-merger `rt=2` rows are `NaN`; `NaN` elsewhere = never escaped |
| `v_eject`     | f8     | km/s          | ejection speed `(V/⟨V⟩)·V*` (set on `rt=1` **and escaped-merger `rt=2`** rows; `NaN` otherwise) |

**Several columns are base-10 logarithms** (`pb`, `semi`, `zl*`, `r*`, `te*`). Convert with
`10**x` — e.g. semi-major axis `a[R☉] = 10**semi`, period `P[day] = 10**pb`.

## 4. Double-compact GR mergers (`record_type = 2`)

Each `rt=2` row is one GR-inspiral merger. The shared columns `time` (= inspiral-config
time), `name1`/`name2`, `m1`/`m2`, `ecc` are set; the full orbit summary is preserved
verbatim in the `mrg_*` columns below; all snapshot-only columns are `NaN`. Rows come from
two sources and are matched to the compiled binaries by their **unordered persistent IDs**
`(id1, id2) ↔ (name1, name2)`:

- **In-cluster mergers** (`orbitd_summary0_in_ext.dat`) — matched to the in-cluster
  (`rt=0`) pair; `kw1`/`kw2` from that pair's last snapshot.
- **Escaped mergers** (the escaped tail of `orbitd_summary0_ext.dat`) — binaries that left
  the cluster and merged outside; matched to the **`rt=1` BINARY ESCAPE record** of the
  same pair, with `kw1`/`kw2` from that record and **`escape_time`/`v_eject` copied onto
  the row**.

> **Telling them apart:** an **escaped-merger `rt=2` row has a finite `escape_time`**
> (copied from its `rt=1` escape record); an **in-cluster-merger `rt=2` row has
> `escape_time = NaN`**. This is the exact, source-based split (counted in the attrs
> `n_merger_escaped` vs `n_merger_incluster`). Using "pair also appears in an `rt=1`
> record" is equivalent *except* for one binary across all 90 sims that genuinely merged
> in-cluster and whose tight remnant-pair then escaped on a post-restart leg (the merger
> was not reproduced after a crash/restart); it is sourced as an in-cluster merger
> (`escape_time = NaN`) but its pair does appear in `rt=1`. So prefer `escape_time` (or
> the attrs) over the pair test when classifying mergers.

**Component types** (`kw1`/`kw2`): from the match above; for any component not thereby
typed compact (an unmatched merger, or one whose last in-cluster snapshot predates its
collapse) the type is set from the component mass via the BSE neutron-star mass ceiling
`MXNS` (file attr `mxns_msun`, 2.5 M☉ in these runs): **mass ≤ MXNS → NS (13), else
BH (14)**. So every `rt=2` row is double-compact-typed.

| column      | units  | meaning (orbitd merger-summary column)                                  |
|-------------|--------|-------------------------------------------------------------------------|
| `mrg_timed` | Myr    | absolute time of the initial inspiral configuration (`timed`, col 1)    |
| `mrg_time`  | Myr    | elapsed inspiral time at this configuration (`time`, col 2)             |
| `mrg_e`     | –      | eccentricity at the inspiral configuration (`e`, col 3)                 |
| `mrg_semi`  | AU     | semi-major axis (`semi`, col 4)                                         |
| `mrg_semir` | R_sch  | semi-major axis in total-Schwarzschild-radius units (`semir`, col 5)   |
| `mrg_edot`  | –      | de/dt (`edot`, col 6; see kozai `adotv2.f`)                            |
| `mrg_adot`  | –      | da/dt (`adot`, col 7)                                                   |
| `mrg_tgr`   | yr     | GR inspiral timescale (`tgr`, col 8)                                    |
| `mrg_fk`    | Hz     | Keplerian orbital frequency (`fk`, col 9)                               |
| `mrg_fgw`   | Hz     | peak GW frequency (`fgw`, col 10)                                       |
| `mrg_m1`    | M☉     | component-1 mass from the orbit integration (`m1`, col 11)             |
| `mrg_m2`    | M☉     | component-2 mass from the orbit integration (`m2`, col 12)             |
| `mrg_mch`   | M☉     | chirp mass (`mch`, col 13)                                             |
| `spin1`     | –      | dimensionless spin of comp 1 (col 18; 1.000 = maximal-spin placeholder for BHs) |
| `spin2`     | –      | dimensionless spin of comp 2 (col 19)                                  |

All `mrg_*` / `spin*` columns are `NaN` on `record_type` 0 and 1.

## 5. Primordial vs. dynamical pairs

Component IDs are assigned sequentially at birth, so a **primordial** binary (born paired)
has consecutive IDs: `abs(name1 - name2) == 1`. Any other pair was **dynamically**
assembled inside the cluster.

## 6. Per-file attributes (metadata)

Open the file's `.attrs` for run-level metadata, including:

| attribute | meaning |
|-----------|---------|
| `source_combo_dir`        | full path of the source simulation directory |
| `source_files`            | `fort.82, fort.821, run.out, orbitd_summary0_in_ext.dat, orbitd_summary0_ext.dat` |
| `format_reference`        | NBODY source files defining the formats |
| `compact_definition`      | the selection rule (`kw1 in {13,14} OR kw2 in {13,14}`) |
| `bh_teff_note`            | `te1/te2 set to NaN for any kw=14 (BH) component` |
| `mxns_msun`               | NS mass ceiling used to type merger components by mass when needed |
| `n_snapshots`             | number of `fort.82` snapshots scanned |
| `n_compact_rows`          | total rows = in-cluster + escape + merger |
| `n_incluster_rows`        | number of `record_type = 0` rows |
| `n_escape_rows`           | number of `record_type = 1` rows |
| `n_merger_rows`           | number of `record_type = 2` rows (in-cluster + escaped) |
| `n_merger_incluster`      | `rt=2` rows from in-cluster mergers |
| `n_merger_tracked` / `n_merger_untracked` | in-cluster mergers matched / not matched to a `rt=0` pair |
| `n_merger_escaped`        | `rt=2` rows from escaped mergers |
| `n_merger_escaped_matched`| escaped mergers matched to a `rt=1` escape record |
| `n_binary_escapes_total`  | all binary escapes in the run (any type) |
| `n_compact_escapers`      | escapers with ≥1 compact component (= `n_escape_rows`) |
| `n_tracked_escapers` / `n_untracked_escapers` | escapers with / without in-cluster history here |
| `time_first_myr`, `time_last_myr` | snapshot time span of the run |
| `tstar_myr_per_nbody`, `vstar_kms_per_nbody`, `rstar_pc_per_nbody` | N-body → physical unit factors (T*, V*, R*) |
| `n_core_blocks`           | number of core-radius RC(t) entries read for `ri_pc` |

## 7. Notes & caveats

- **In-cluster period is capped.** `hrplot.f` clips the period at 99999.9 day, so `pb`
  saturates at `log10(99999.9) ≈ 5.0` for wide in-cluster binaries; the **escape-row** `pb`
  is *not* capped.
- **Radial distance:** `ri` is in core radii; `ri_pc = ri × RC(t) × R*` with `RC(t)` from
  the run's OUTPUT diagnostics at the nearest time (within ~1 N-body time unit) and `R*`
  the N-body length unit in pc.
- **Escape rows carry only orbital/type/mass info**; `ri`, `ri_pc`, `zl*`, `r*`, `te*` are
  `NaN`, and `semi` is Kepler-derived.
- **Escape-time precision.** `escape_time = (preceding ADJUST time) × T*`, with `T*` to 3
  significant figures, so absolute escape times carry ~0.1–0.3 % uncertainty.
- **Merger rows are an overlay**, not snapshots: they reuse `time`/`name1`/`name2`/`m1`/
  `m2`/`ecc` for convenience and joining, but the inspiral physics lives in `mrg_*`.
- **One post-restart edge case** (pair 8388/8394 in `M50k_rh1_1201_Z0002`): a BBH that
  genuinely merged in-cluster, after which the run crashed; on restart from the last
  snapshot the merger was not reproduced (truncation/thread-count differences) and the
  surviving tight pair later escaped. It is kept as an **in-cluster** merger (its true
  event; `escape_time = NaN` on the merger row), even though the pair also has an `rt=1`
  escape record — hence the recommendation to classify mergers by `escape_time`.
- **Name order can swap** between rows of the same binary; match on the unordered pair.

## 8. Quick start (Python)

```python
import h5py, numpy as np, pandas as pd

with h5py.File("M75k_rh2_1502_Z005_compact_binaries.h5", "r") as f:
    g = f["compact"]
    df = pd.DataFrame({k: g[k][:] for k in g.keys()})
    meta = dict(f.attrs)

incluster = df[df.record_type == 0]
escapers  = df[df.record_type == 1]
mergers   = df[df.record_type == 2]

# physical values from the log10 columns (in-cluster / escape rows)
df["a_Rsun"] = 10.0 ** df["semi"]      # semi-major axis [R_sun]
df["P_day"]  = 10.0 ** df["pb"]        # orbital period  [day]

# binary identity, primordial vs dynamical
pair = np.sort(df[["name1", "name2"]].to_numpy(), axis=1)
df["pair"]       = list(map(tuple, pair))
df["primordial"] = np.abs(df.name1 - df.name2) == 1

# split mergers into escaped vs in-cluster: escaped-merger rows have a finite
# escape_time, in-cluster-merger rows have NaN (the exact source-based split)
mergers = mergers.assign(escaped=np.isfinite(mergers.escape_time))
print(mergers[["name1", "name2", "kw1", "kw2", "m1", "m2", "mrg_e", "mrg_fgw",
               "spin1", "spin2", "escape_time", "escaped"]])

# follow one binary's evolution, time-ordered
for key, trk in incluster.groupby("pair"):
    trk = trk.sort_values("time")
    # trk.time, trk.a_Rsun, trk.ecc, ...
```

---

*Generated by `extract_compact.py` / `sweep_compact.py`. Questions: sambaran.banerjee@gmail.com*
