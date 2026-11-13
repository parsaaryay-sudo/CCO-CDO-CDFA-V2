"""Pure calculation functions for the CCO / CDO / CDFA lab.

No Streamlit or Plotly imports here, so everything can be unit-tested.
All helper formulas are *educational approximations*, not procedure-design tools.
"""
from __future__ import annotations

import math
from itertools import combinations

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
FT_PER_NM = 6076.12                      # feet in one nautical mile
GUIDE_LEVEL_SECONDS = 217                # guide, section 7.2: avg level flight per non-CDO arrival
GUIDE_EXTRA_FUEL_KG = 46                 # guide, section 7.2: extra fuel per non-CDO arrival
# Fuel burned per minute of level flight implied by the guide's two numbers (46 kg / 217 s)
GUIDE_KG_PER_MIN = GUIDE_EXTRA_FUEL_KG / (GUIDE_LEVEL_SECONDS / 60.0)
# The guide only says a level segment in CLIMB burns "significantly more" than one in DESCENT.
# This default (about 2x the descent value) is an assumption for teaching purposes.
DEFAULT_CLIMB_LEVEL_KG_PER_MIN = 25.0
RULE_OF_THUMB_NM_PER_1000FT = 3.0        # TOD rule of thumb requested for the CDO simulator
STABILIZED_MAX_FPM = 1000.0              # guide, section 3.3: "typically under 1,000 fpm"
VDA_MIN, VDA_MAX, VDA_DEFAULT = 2.75, 3.77, 3.0   # guide, section 3.3


# ----------------------------------------------------------------------------
# Generic vertical-profile builder
# ----------------------------------------------------------------------------
def build_knots(start_alt: float, segments: list) -> tuple[np.ndarray, np.ndarray]:
    """Turn segments into (time, altitude) knots.

    segments: ("vs", target_alt_ft, rate_fpm)  -> climb/descend to target at |rate|
              ("level", minutes)               -> hold current altitude
    """
    t, a, cur = [0.0], [float(start_alt)], float(start_alt)
    for seg in segments:
        if seg[0] == "vs":
            target, rate = float(seg[1]), abs(float(seg[2]))
            if rate <= 0 or target == cur:
                continue
            t.append(t[-1] + abs(target - cur) / rate)  # time = altitude change / rate
            a.append(target)
            cur = target
        elif seg[0] == "level":
            minutes = max(0.0, float(seg[1]))
            if minutes > 0:
                t.append(t[-1] + minutes)
                a.append(cur)
    return np.array(t), np.array(a)


def profile_from_segments(start_alt: float, segments: list, gs_kt: float,
                          step_min: float = 0.05) -> pd.DataFrame:
    """Sample a segment list on a regular time grid (plus the knots themselves)."""
    kt, ka = build_knots(start_alt, segments)
    grid = np.unique(np.concatenate([np.arange(0.0, kt[-1], step_min), kt]))
    return pd.DataFrame({
        "time_min": grid,
        "dist_nm": grid * gs_kt / 60.0,          # distance = GS x time (constant GS, no wind)
        "alt_ft": np.interp(grid, kt, ka),
    })


def intervals_from_mask(t: np.ndarray, mask: np.ndarray) -> list[tuple[float, float, int, int]]:
    """Contiguous True runs -> (t_start, t_end, i_start, i_end)."""
    out, start = [], None
    for i, m in enumerate(mask):
        if m and start is None:
            start = i
        if (not m) and start is not None:
            out.append((float(t[start]), float(t[i - 1]), start, i - 1))
            start = None
    if start is not None:
        out.append((float(t[start]), float(t[len(mask) - 1]), start, len(mask) - 1))
    return out


# ----------------------------------------------------------------------------
# A) CCO
# ----------------------------------------------------------------------------
def validate_cco(cruise_alt, elev, rate, gs, levels) -> list[str]:
    errs = []
    if cruise_alt <= elev:
        errs.append("Initial cruise altitude must be higher than the airport elevation.")
    if rate <= 0:
        errs.append("Climb rate must be greater than zero.")
    if gs <= 0:
        errs.append("Ground speed must be greater than zero.")
    for i, (alt, mins) in enumerate(levels, start=1):
        if not (elev < alt < cruise_alt):
            errs.append(f"Level-off {i}: altitude {alt:,.0f} ft must be between the airport "
                        f"elevation ({elev:,.0f} ft) and the cruise altitude ({cruise_alt:,.0f} ft).")
        if mins <= 0:
            errs.append(f"Level-off {i}: duration must be greater than zero.")
    alts = [a for a, _ in levels]
    if len(set(alts)) != len(alts):
        errs.append("Level-off altitudes must all be different.")
    return errs


def cco_profiles(cruise_alt, elev, rate, gs, levels):
    """Continuous climb vs stepped climb. levels = [(alt_ft, minutes), ...]."""
    levels = sorted(levels)
    cont = profile_from_segments(elev, [("vs", cruise_alt, rate)], gs)
    segs = []
    for alt, mins in levels:
        segs += [("vs", alt, rate), ("level", mins)]
    segs.append(("vs", cruise_alt, rate))
    step = profile_from_segments(elev, segs, gs)
    return cont, step


def cco_summary(cont, step, levels, kg_per_min) -> dict:
    t_c, t_s = cont.time_min.iloc[-1], step.time_min.iloc[-1]
    level_min = sum(m for _, m in levels)
    return dict(t_cont=t_c, t_step=t_s, d_cont=cont.dist_nm.iloc[-1], d_step=step.dist_nm.iloc[-1],
                dt=t_s - t_c, level_min=level_min,
                extra_fuel=level_min * kg_per_min)   # educational approximation


# ----------------------------------------------------------------------------
# B) CDO
# ----------------------------------------------------------------------------
def cdo_ft_per_nm(mode: str, angle_deg: float) -> float:
    """Descent gradient in ft per NM: rule of thumb (1000 ft per 3 NM) or from an angle."""
    if mode == "rule":
        return 1000.0 / RULE_OF_THUMB_NM_PER_1000FT
    return math.tan(math.radians(angle_deg)) * FT_PER_NM


def validate_cdo(start_alt, faf_alt, gs, n_steps, level_nm) -> list[str]:
    errs = []
    if start_alt <= faf_alt:
        errs.append("Start altitude must be higher than the FAF altitude.")
    if gs <= 0:
        errs.append("Ground speed must be greater than zero.")
    if n_steps > 0 and level_nm <= 0:
        errs.append("Level-off length must be greater than zero when step-downs are used.")
    return errs


def cdo_profiles(start_alt, faf_alt, gs, n_steps, level_nm, ft_per_nm):
    """CDO vs step-down profile, both ending at the FAF at the same time.

    Both aircraft start at the same point. The CDO aircraft stays high longer and starts its
    idle descent later (at TOD); the step-down aircraft descends early and levels off n times.
    """
    drop = start_alt - faf_alt
    d_desc = drop / ft_per_nm                    # horizontal distance of the descent itself
    rod = gs * ft_per_nm / 60.0                  # ft/min = (NM/min) x (ft/NM)
    total_level_nm = n_steps * level_nm
    total_nm = d_desc + total_level_nm

    cdo = profile_from_segments(start_alt, [("level", total_level_nm / gs * 60.0),
                                            ("vs", faf_alt, rod)], gs)
    segs = []
    for i in range(1, n_steps + 1):
        segs += [("vs", start_alt - i * drop / (n_steps + 1), rod), ("level", level_nm / gs * 60.0)]
    segs.append(("vs", faf_alt, rod))
    step = profile_from_segments(start_alt, segs, gs)
    for df in (cdo, step):
        df["to_go_nm"] = total_nm - df["dist_nm"]  # distance still to fly to the FAF
    return cdo, step, dict(drop=drop, d_desc=d_desc, rod=rod, total_nm=total_nm,
                           total_level_nm=total_level_nm,
                           tod_rule_nm=drop / 1000.0 * RULE_OF_THUMB_NM_PER_1000FT)


def cdo_summary(info, gs, kg_per_min) -> dict:
    level_min = info["total_level_nm"] / gs * 60.0
    return dict(level_s=level_min * 60.0, level_nm=info["total_level_nm"],
                extra_fuel=level_min * kg_per_min)


def dtg_altitude(dtg_nm: float, elev_ft: float, angle_deg: float = 3.0) -> float:
    """Suggested altitude on a 3-degree path: elevation + DTG x tan(angle) x ft/NM."""
    return elev_ft + dtg_nm * math.tan(math.radians(angle_deg)) * FT_PER_NM


# ----------------------------------------------------------------------------
# C) CDFA
# ----------------------------------------------------------------------------
def terrain_profile(x, base, peak, x_peak, half_width):
    """Flat terrain at `base` plus one triangular ridge (educational terrain model)."""
    x = np.asarray(x, dtype=float)
    return base + max(0.0, peak - base) * np.maximum(0.0, 1.0 - np.abs(x - x_peak) / half_width)


def validate_cdfa(faf_alt, thr_elev, mda, vda, gs, buffer, dive_rate) -> list[str]:
    errs = []
    if not (VDA_MIN <= vda <= VDA_MAX):
        errs.append(f"VDA must be between {VDA_MIN} and {VDA_MAX} degrees.")
    if faf_alt <= thr_elev:
        errs.append("FAF altitude must be higher than the runway threshold elevation.")
    if not (thr_elev < mda < faf_alt):
        errs.append("MDA must be above the threshold elevation and below the FAF altitude.")
    if buffer < 0:
        errs.append("DDA buffer cannot be negative.")
    if mda + buffer >= faf_alt:
        errs.append("DDA (MDA + buffer) must be below the FAF altitude.")
    if gs <= 0 or dive_rate <= 0:
        errs.append("Ground speed and dive rate must be greater than zero.")
    if errs:
        return errs
    ft_nm = math.tan(math.radians(vda)) * FT_PER_NM
    rod = gs * ft_nm / 60.0
    if dive_rate <= rod:
        errs.append(f"Dive rate ({dive_rate:,.0f} ft/min) must exceed the CDFA rate ({rod:,.0f} ft/min), "
                    "otherwise the dive-and-drive aircraft never reaches MDA before the CDFA path does.")
        return errs
    d_faf = (faf_alt - thr_elev) / ft_nm
    x_dive_end = d_faf - (faf_alt - mda) / dive_rate * gs / 60.0
    if x_dive_end - (mda - thr_elev) / ft_nm < 0.05:
        errs.append("Dive rate is too low: the aircraft would reach MDA almost exactly where the "
                    "descent path crosses MDA, so there is no level segment. Increase the dive rate.")
    return errs


def cdfa_geometry(faf_alt, thr_elev, mda, vda, gs, buffer, dive_rate) -> dict:
    ft_nm = math.tan(math.radians(vda)) * FT_PER_NM
    d_faf = (faf_alt - thr_elev) / ft_nm
    d_mda = (mda - thr_elev) / ft_nm
    d_dda = (mda + buffer - thr_elev) / ft_nm
    x_dive_end = d_faf - (faf_alt - mda) / dive_rate * gs / 60.0
    return dict(ft_nm=ft_nm, d_faf=d_faf, d_mda=d_mda, d_dda=d_dda, dda=mda + buffer,
                rod=gs * ft_nm / 60.0,                 # ft/min = GS(kt) x 101.27 x tan(VDA)
                x_dive_end=x_dive_end, level_nm=x_dive_end - d_mda,
                level_min=(x_dive_end - d_mda) / gs * 60.0)


def cdfa_profiles(g: dict, faf_alt, thr_elev, mda, gs):
    """Both profiles on a distance-to-threshold axis, with time since FAF."""
    xs = np.linspace(0.0, g["d_faf"], 600)
    knots_x = np.array([g["d_faf"], g["x_dive_end"], g["d_mda"], 0.0])
    knots_a = np.array([faf_alt, mda, mda, thr_elev])
    xd = np.unique(np.concatenate([xs, knots_x]))
    dd_alt = np.interp(xd, knots_x[::-1], knots_a[::-1])      # xp must be increasing
    cdfa_alt = thr_elev + xd * g["ft_nm"]
    mk = lambda alt: pd.DataFrame({"to_go_nm": xd[::-1], "alt_ft": alt[::-1],
                                   "time_min": (g["d_faf"] - xd[::-1]) / gs * 60.0})
    return mk(cdfa_alt), mk(dd_alt)


def cfit_zones(x_from, x_to, level_alt, terrain_fn, low_agl):
    """Intervals on the level segment where height above terrain is below the alert value."""
    xs = np.linspace(x_to, x_from, 800)
    mask = (level_alt - terrain_fn(xs)) < low_agl
    return [(float(xs[a]), float(xs[b])) for _, _, a, b in intervals_from_mask(xs, mask)]


# ----------------------------------------------------------------------------
# D) SID / STAR crossing
# ----------------------------------------------------------------------------
def make_aircraft(name, p0, p1, speed, t_start, start_alt, target_alt, rate) -> dict:
    p0, p1 = np.array(p0, float), np.array(p1, float)
    return dict(name=name, p0=p0, p1=p1, length=float(np.hypot(*(p1 - p0))), speed=float(speed),
                t_start=float(t_start), start_alt=float(start_alt), target_alt=float(target_alt),
                rate=float(rate), knots=build_knots(start_alt, [("vs", target_alt, rate)]),
                hold_min=0.0, level_alt=None)


def aircraft_state(ac: dict, t: np.ndarray):
    """Position/altitude on the route; NaN before departure and after leaving the route."""
    L = ac["length"]
    ux, uy = (ac["p1"] - ac["p0"]) / L
    tr = t - ac["t_start"]
    s = tr * ac["speed"] / 60.0                       # distance along route (NM)
    vis = (tr >= 0) & (s <= L + 1e-9)
    sc = np.clip(s, 0, L)
    x = np.where(vis, ac["p0"][0] + ux * sc, np.nan)
    y = np.where(vis, ac["p0"][1] + uy * sc, np.nan)
    alt = np.where(vis, np.interp(np.maximum(tr, 0.0), *ac["knots"]), np.nan)
    return x, y, alt


def sim_time_grid(*acs, step_min=0.05) -> np.ndarray:
    t_end = max(a["t_start"] + a["length"] / a["speed"] * 60.0 for a in acs)
    return np.arange(0.0, t_end + step_min, step_min)


def pair_metrics(sa, sb, min_h, min_v):
    """Horizontal (NM), vertical (ft) distance and violation flag (both below minima)."""
    with np.errstate(invalid="ignore"):
        h = np.hypot(sa[0] - sb[0], sa[1] - sb[1])
        v = np.abs(sa[2] - sb[2])
        viol = (h < min_h) & (v < min_v)
    return h, v, viol


def seg_intersection(p0, p1, q0, q1):
    """Intersection of two route segments -> (distance along P, distance along Q, point) or None."""
    p0, p1, q0, q1 = (np.array(v, float) for v in (p0, p1, q0, q1))
    r, s = p1 - p0, q1 - q0
    cross = lambda a, b: a[0] * b[1] - a[1] * b[0]
    den = cross(r, s)
    if abs(den) < 1e-9:
        return None
    t = cross(q0 - p0, s) / den
    u = cross(q0 - p0, r) / den
    if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
        return t * np.hypot(*r), u * np.hypot(*s), p0 + t * r
    return None


def apply_level_off(ac: dict, level_alt: float, s_cross: float, release_nm: float) -> dict:
    """Level the aircraft at level_alt until it is `release_nm` past the crossing point."""
    lo, hi = sorted((ac["start_alt"], ac["target_alt"]))
    if not (lo < level_alt < hi):
        return ac
    t_release = (s_cross + release_nm) / ac["speed"] * 60.0        # minutes since its own start
    t_reach = abs(level_alt - ac["start_alt"]) / ac["rate"]
    hold = max(0.0, t_release - t_reach)
    segs = [("vs", level_alt, ac["rate"]), ("level", hold), ("vs", ac["target_alt"], ac["rate"])]
    return {**ac, "knots": build_knots(ac["start_alt"], segs), "hold_min": hold, "level_alt": float(level_alt)}


def best_level_off(which, dep, arr, t, min_h, min_v, s_cross_dep, s_cross_arr, release_nm, step_ft=100):
    """Search level-off altitudes (every step_ft) for the one that removes the violation
    with the shortest level segment. Returns the modified aircraft dict or None."""
    ac, s_cross = (dep, s_cross_dep) if which == "dep" else (arr, s_cross_arr)
    lo, hi = sorted((ac["start_alt"], ac["target_alt"]))
    best = None
    for level in np.arange(lo + step_ft, hi, step_ft):
        mod = apply_level_off(ac, float(level), s_cross, release_nm)
        a, b = (mod, arr) if which == "dep" else (dep, mod)
        if not pair_metrics(aircraft_state(a, t), aircraft_state(b, t), min_h, min_v)[2].any():
            if best is None or mod["hold_min"] < best["hold_min"]:
                best = mod
    return best


# ----------------------------------------------------------------------------
# E) Multi-aircraft
# ----------------------------------------------------------------------------
MULTI_COLUMNS = ["Callsign", "Type", "Start X (NM)", "Start Y (NM)", "Heading (deg)", "Speed (kt)",
                 "Start alt (ft)", "V/S (ft/min)", "Target alt (ft)", "Start offset (min)"]


def default_multi_table() -> pd.DataFrame:
    rows = [
        ("DEP1", "Departure", 0.0, 0.0, 45.0, 240.0, 1000.0, 1800.0, 15000.0, 0.0),
        ("ARR1", "Arrival", 36.0, -3.0, 315.0, 260.0, 22000.0, 1500.0, 4000.0, 0.0),
        ("DEP2", "Departure", -25.0, 20.0, 90.0, 230.0, 1000.0, 1500.0, 12000.0, 0.0),
        ("ARR2", "Arrival", 20.0, 45.0, 180.0, 250.0, 9000.0, 1200.0, 3000.0, 0.0),
    ]
    return pd.DataFrame(rows, columns=MULTI_COLUMNS)


def validate_multi(df: pd.DataFrame) -> list[str]:
    errs = []
    if not (3 <= len(df) <= 6):
        errs.append("Enter between 3 and 6 aircraft.")
        return errs
    if df.isna().any().any():
        errs.append("Every cell must be filled in (no empty values).")
        return errs
    if df["Callsign"].astype(str).str.strip().eq("").any() or df["Callsign"].duplicated().any():
        errs.append("Callsigns must be non-empty and unique.")
    for _, r in df.iterrows():
        cs = r["Callsign"]
        if r["Type"] not in ("Departure", "Arrival"):
            errs.append(f"{cs}: type must be Departure or Arrival.")
        if r["Speed (kt)"] <= 0:
            errs.append(f"{cs}: speed must be greater than zero.")
        if r["V/S (ft/min)"] <= 0:
            errs.append(f"{cs}: enter the climb/descent rate as a positive number.")
        if r["Type"] == "Departure" and r["Target alt (ft)"] <= r["Start alt (ft)"]:
            errs.append(f"{cs}: a departure needs a target altitude above its start altitude.")
        if r["Type"] == "Arrival" and r["Target alt (ft)"] >= r["Start alt (ft)"]:
            errs.append(f"{cs}: an arrival needs a target altitude below its start altitude.")
    return errs


def multi_states(df: pd.DataFrame, t: np.ndarray) -> dict:
    out = {}
    for _, r in df.iterrows():
        tr = t - r["Start offset (min)"]
        vis = tr >= 0
        h = math.radians(r["Heading (deg)"])
        s = np.maximum(tr, 0) * r["Speed (kt)"] / 60.0
        x = np.where(vis, r["Start X (NM)"] + math.sin(h) * s, np.nan)   # heading 0 = north, 90 = east
        y = np.where(vis, r["Start Y (NM)"] + math.cos(h) * s, np.nan)
        delta = r["V/S (ft/min)"] * np.maximum(tr, 0)
        if r["Target alt (ft)"] >= r["Start alt (ft)"]:
            alt = np.minimum(r["Start alt (ft)"] + delta, r["Target alt (ft)"])
        else:
            alt = np.maximum(r["Start alt (ft)"] - delta, r["Target alt (ft)"])
        out[r["Callsign"]] = (x, y, np.where(vis, alt, np.nan))
    return out


def multi_conflicts(states: dict, t, min_h, min_v):
    """All pairs: metrics per pair plus a list of conflict episodes."""
    pairs, episodes = {}, []
    for a, b in combinations(states, 2):
        h, v, viol = pair_metrics(states[a], states[b], min_h, min_v)
        pairs[(a, b)] = (h, v, viol)
        for t0, t1, i0, i1 in intervals_from_mask(t, viol):
            episodes.append(dict(Pair=f"{a} / {b}", From_min=round(t0, 2), To_min=round(t1, 2),
                                 Min_horizontal_NM=round(float(np.nanmin(h[i0:i1 + 1])), 2),
                                 Min_vertical_ft=round(float(np.nanmin(v[i0:i1 + 1])), 0)))
    return pairs, episodes
