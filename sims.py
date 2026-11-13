"""Streamlit UI for the five simulators. All maths lives in physics.py, all figures in charts.py."""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

import charts
import physics as P
from theme import callout, metric_card, metric_grid

STATUS_BY_BOOL = {True: "warn", False: "ok"}


# ----------------------------------------------------------------------------
# Small UI helpers
# ----------------------------------------------------------------------------
def is_pres() -> bool:
    return bool(st.session_state.get("w_pres", False))


def init(defaults: dict) -> None:
    """Put defaults into session_state once (widgets then use their key, no `value=` needed)."""
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def _reset(defaults: dict) -> None:
    for k, v in defaults.items():
        st.session_state[k] = v


def reset_button(tag: str, defaults: dict) -> None:
    with st.container(key=f"sec-reset-{tag}"):       # "sec-" containers are hidden in Presentation Mode
        st.button("Reset to defaults", key=f"sec-resetbtn-{tag}", on_click=_reset, args=(defaults,))


def num(label, key, lo, hi, step, fmt=None, help=None):
    return st.number_input(label, min_value=lo, max_value=hi, step=step, key=key, format=fmt, help=help)


def show_fig(fig, key: str) -> None:
    try:
        st.plotly_chart(fig, width="stretch", config=charts.PLOT_CONFIG, key=key)
    except Exception:                                   # older Streamlit versions
        st.plotly_chart(fig, use_container_width=True, config=charts.PLOT_CONFIG, key=key)


def show_table(df, **kw) -> None:
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except Exception:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


def csv_button(df: pd.DataFrame, filename: str, tag: str) -> None:
    with st.container(key=f"sec-dl-{tag}"):
        st.download_button("Download chart data (CSV)", df.to_csv(index=False).encode("utf-8"),
                           file_name=filename, mime="text/csv", key=f"sec-dlbtn-{tag}")
        st.caption("Chart image: use the camera icon in the chart toolbar (top right of the chart).")


def formulas_box(tag: str, markdown: str) -> None:
    with st.container(key=f"sec-formulas-{tag}"):
        with st.expander("Formulas and assumptions"):
            st.markdown(markdown)
            st.markdown("*Educational approximation. Not for real ATC operations or procedure design.*")


def show_errors(errs: list[str]) -> bool:
    for e in errs:
        st.error(e)
    return bool(errs)


# ----------------------------------------------------------------------------
# A) CCO simulator
# ----------------------------------------------------------------------------
CCO_DEF = {"w_cco_fl": 350, "w_cco_elev": 0, "w_cco_gs": 300, "w_cco_mode": "Climb rate (ft/min)",
           "w_cco_rate": 2000, "w_cco_grad": 400, "w_cco_n": 2, "w_cco_fuel": 25.0,
           "w_cco_a1": 6000, "w_cco_m1": 2.0, "w_cco_a2": 10000, "w_cco_m2": 3.0,
           "w_cco_a3": 14000, "w_cco_m3": 2.0, "w_cco_a4": 18000, "w_cco_m4": 2.0}


def sim_cco() -> None:
    init(CCO_DEF)
    st.markdown("### CCO simulator")
    st.caption("Change any number and the chart updates. Defaults already show a result.")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            fl = num("Initial cruise level (FL)", "w_cco_fl", 100, 450, 10)
            elev = num("Airport elevation (ft)", "w_cco_elev", 0, 6000, 100)
            gs = num("Average ground speed in climb (kt)", "w_cco_gs", 150, 500, 10)
            mode = st.radio("Climb input", ["Climb rate (ft/min)", "Climb gradient (ft/NM)"], key="w_cco_mode", horizontal=True)
            if mode == "Climb rate (ft/min)":
                rate = float(num("Climb rate (ft/min)", "w_cco_rate", 500, 6000, 100))
            else:
                grad = num("Climb gradient (ft/NM)", "w_cco_grad", 100, 1500, 10)
                rate = grad * gs / 60.0                      # ft/min = ft/NM x NM/min
                st.caption(f"Equivalent climb rate: {rate:,.0f} ft/min")
        with c2:
            n = st.slider("Number of ATC level-offs (step-ups)", min_value=0, max_value=4, step=1, key="w_cco_n")
            for i in range(1, n + 1):
                a, b = st.columns(2)
                with a:
                    num(f"Level-off {i} altitude (ft)", f"w_cco_a{i}", 500, 45000, 500)
                with b:
                    num(f"Level-off {i} duration (min)", f"w_cco_m{i}", 0.5, 15.0, 0.5, "%.1f")
            with st.expander("Fuel model (editable, educational approximation)"):
                num("Extra fuel per minute of level flight in climb (kg/min)", "w_cco_fuel", 1.0, 200.0, 1.0, "%.1f",
                    help="Assumption, not from the guide. The guide only says a level segment in climb burns "
                         "significantly more fuel than one in descent.")
    reset_button("cco", CCO_DEF)

    levels = [(float(st.session_state[f"w_cco_a{i}"]), float(st.session_state[f"w_cco_m{i}"])) for i in range(1, n + 1)]
    cruise = float(fl * 100)
    if show_errors(P.validate_cco(cruise, float(elev), rate, float(gs), levels)):
        return
    cont, step = P.cco_profiles(cruise, float(elev), rate, float(gs), levels)
    s = P.cco_summary(cont, step, levels, float(st.session_state["w_cco_fuel"]))
    extra = s["dt"] > 1e-9
    st.markdown(metric_grid([
        metric_card("Time to Top of Climb (CCO)", f"{s['t_cont']:.1f}", "min", "ok", f"{s['d_cont']:.0f} NM flown"),
        metric_card("Time to Top of Climb (stepped)", f"{s['t_step']:.1f}", "min", STATUS_BY_BOOL[extra], f"{s['d_step']:.0f} NM flown"),
        metric_card("Time difference", f"+{s['dt']:.1f}", "min", STATUS_BY_BOOL[extra], f"{s['d_step'] - s['d_cont']:.0f} NM extra distance"),
        metric_card("Estimated extra fuel", f"{s['extra_fuel']:.0f}", "kg", STATUS_BY_BOOL[extra], "Educational approximation"),
    ]), unsafe_allow_html=True)
    show_fig(charts.cco_figure(cont, step, cruise, is_pres()), "fig_cco")
    out = pd.concat([cont.assign(profile="Continuous climb (CCO)"), step.assign(profile="Stepped climb")])
    csv_button(out, "cco_profiles.csv", "cco")
    formulas_box("cco", """
- Time to climb = altitude change / climb rate. Distance = ground speed x time / 60 (constant ground speed, no wind).
- Gradient input: climb rate (ft/min) = gradient (ft/NM) x ground speed (kt) / 60.
- Stepped climb = the same climb rate, plus a level segment of the entered duration at each level-off altitude.
- Time difference = sum of the level-off durations.
- Extra fuel = total level time (min) x the fuel factor (kg/min). The factor is an editable assumption (default 25 kg/min, about twice the descent value derived from the guide).
- Ignored: acceleration, thrust changes, wind, aircraft type, weight and speed restrictions.""")


# ----------------------------------------------------------------------------
# B) CDO simulator (+ Distance-to-Go helper)
# ----------------------------------------------------------------------------
CDO_RULE = "Rule of thumb (3 NM per 1,000 ft)"
CDO_ANGLE = "Descent angle (degrees)"
CDO_DEF = {"w_cdo_start": 10000, "w_cdo_faf": 3000, "w_cdo_gs": 220, "w_cdo_mode": CDO_RULE, "w_cdo_angle": 3.0,
           "w_cdo_n": 2, "w_cdo_len": 5.0, "w_cdo_fuel": round(P.GUIDE_KG_PER_MIN, 1)}
DTG_DEF = {"w_dtg_dist": 25.0, "w_dtg_elev": 0, "w_dtg_use": True, "w_dtg_cur": 9000}


def sim_cdo() -> None:
    init(CDO_DEF)
    st.markdown("### CDO simulator")
    st.caption("Both aircraft start together and reach the FAF at the same time. Only the vertical profile differs.")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            start = num("Cruise / start altitude (ft)", "w_cdo_start", 3000, 45000, 500)
            faf = num("FAF altitude (ft)", "w_cdo_faf", 500, 10000, 100)
            gs = num("Ground speed (kt)", "w_cdo_gs", 120, 450, 5)
            mode = st.radio("Descent gradient", [CDO_RULE, CDO_ANGLE], key="w_cdo_mode")
            angle = 3.0
            if mode == CDO_ANGLE:
                angle = float(st.slider("Descent angle (degrees)", min_value=1.5, max_value=5.0, step=0.1, key="w_cdo_angle"))
        with c2:
            n = st.slider("Number of step-down level-offs", min_value=0, max_value=4, step=1, key="w_cdo_n")
            length = num("Length of each level-off (NM)", "w_cdo_len", 1.0, 20.0, 0.5, "%.1f")
            with st.expander("Fuel model (editable)"):
                num("Extra fuel per minute of level flight in descent (kg/min)", "w_cdo_fuel", 1.0, 100.0, 0.1, "%.1f",
                    help="Default derived from the guide: 46 kg / 217 s = 12.7 kg per minute.")
    reset_button("cdo", CDO_DEF)

    ft_nm = P.cdo_ft_per_nm("rule" if mode == CDO_RULE else "angle", angle)
    if show_errors(P.validate_cdo(float(start), float(faf), float(gs), n, float(length))):
        return
    cdo, step, info = P.cdo_profiles(float(start), float(faf), float(gs), n, float(length), ft_nm)
    s = P.cdo_summary(info, float(gs), float(st.session_state["w_cdo_fuel"]))
    lvl = s["level_nm"] > 0
    st.markdown(metric_grid([
        metric_card("Top of Descent distance", f"{info['d_desc']:.1f}", "NM", "ok",
                    f"Rule of thumb (3 NM per 1,000 ft): {info['tod_rule_nm']:.1f} NM"),
        metric_card("Descent rate", f"{info['rod']:,.0f}", "ft/min", None, "Same rate used in both profiles"),
        metric_card("Level flight (step-down)", f"{s['level_s']:.0f}", "s", STATUS_BY_BOOL[lvl], f"{s['level_nm']:.1f} NM at low altitude"),
        metric_card("Estimated extra fuel", f"{s['extra_fuel']:.0f}", "kg", STATUS_BY_BOOL[lvl], "Educational approximation"),
    ]), unsafe_allow_html=True)
    st.markdown(callout(
        f"<b>Guide reference (section 7.2, source: the supplied guide file):</b> flights flying non-CDO profiles lose an average of "
        f"<b>{P.GUIDE_LEVEL_SECONDS} s</b> in low-altitude level flight and waste <b>{P.GUIDE_EXTRA_FUEL_KG} kg</b> of extra fuel per arrival. "
        f"Your step-down profile: <b>{s['level_s']:.0f} s</b> and <b>{s['extra_fuel']:.0f} kg</b>.", "info"), unsafe_allow_html=True)
    show_fig(charts.cdo_figure(cdo, step, float(start), float(faf), info["d_desc"], is_pres()), "fig_cdo")
    out = pd.concat([cdo.assign(profile="CDO"), step.assign(profile="Step-down")])
    csv_button(out, "cdo_profiles.csv", "cdo")
    formulas_box("cdo", """
- Descent gradient: rule of thumb = 1,000 ft per 3 NM (about 333 ft/NM, roughly 3.1 degrees), or tan(angle) x 6,076 ft/NM.
- TOD distance = (start altitude - FAF altitude) / gradient. The rule-of-thumb value is always shown for comparison.
- Descent rate (ft/min) = ground speed (kt) / 60 x gradient (ft/NM).
- Step-down profile: the altitude to lose is split evenly between the level-offs; each level-off has the entered length. Level time = total level NM / ground speed.
- Extra fuel = level time (min) x fuel factor (default 12.7 kg/min, derived from the guide: 46 kg in 217 s).
- Ignored: speed changes, wind, configuration and drag, aircraft type.""")
    st.divider()
    sim_dtg()


def sim_dtg() -> None:
    init(DTG_DEF)
    st.markdown("#### Distance-to-Go helper")
    st.caption("Enter the distance to the airport to see the suggested altitude on a 3-degree path.")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            dist = num("Distance to the airport (NM)", "w_dtg_dist", 1.0, 150.0, 1.0, "%.1f")
        with c2:
            elev = num("Airport elevation (ft)", "w_dtg_elev", 0, 6000, 100)
        with c3:
            use = st.checkbox("Compare with a current altitude", key="w_dtg_use")
            cur = num("Current altitude (ft)", "w_dtg_cur", 0, 45000, 100) if use else None
    reset_button("dtg", DTG_DEF)
    path = lambda x: P.dtg_altitude(x, float(elev), 3.0)
    suggested = path(float(dist))
    rule = float(elev) + float(dist) * 1000.0 / P.RULE_OF_THUMB_NM_PER_1000FT
    cards = [metric_card("Suggested altitude (3-degree path)", f"{suggested:,.0f}", "ft", "ok", f"At {dist:.0f} NM to go"),
             metric_card("Rule-of-thumb altitude", f"{rule:,.0f}", "ft", None, "1,000 ft per 3 NM")]
    if cur is not None:
        diff = cur - suggested
        if abs(diff) <= 300:
            cards.append(metric_card("Versus 3-degree path", "On path", "", "ok", f"{diff:+,.0f} ft (tolerance 300 ft, assumed)"))
        else:
            cards.append(metric_card("Versus 3-degree path", f"{abs(diff):,.0f}", "ft " + ("above" if diff > 0 else "below"), "warn",
                                     "Energy needs managing; DTG helps the crew"))
    st.markdown(metric_grid(cards), unsafe_allow_html=True)
    show_fig(charts.dtg_figure(float(dist), float(elev), cur, path, is_pres()), "fig_dtg")
    formulas_box("dtg", """
- Suggested altitude = airport elevation + distance x tan(3 degrees) x 6,076 ft/NM (about 319 ft per NM).
- The 300 ft on/above/below tolerance is an assumption for this lab, not a value from the guide.
- The guide stresses that accurate Distance-to-Go lets crews and the FMS manage kinetic and potential energy during vectoring.""")


# ----------------------------------------------------------------------------
# C) CDFA simulator
# ----------------------------------------------------------------------------
CDFA_DEF = {"w_cdfa_faf": 2000, "w_cdfa_thr": 100, "w_cdfa_mda": 600, "w_cdfa_vda": 3.0, "w_cdfa_gs": 120,
            "w_cdfa_buf": 50, "w_cdfa_dive": 1500, "w_cdfa_ter": True, "w_cdfa_peak": 500, "w_cdfa_xpeak": 3.0,
            "w_cdfa_hw": 1.5, "w_cdfa_low": 250}


def sim_cdfa() -> None:
    init(CDFA_DEF)
    st.markdown("### CDFA simulator")
    st.caption("Distance is measured to the runway threshold. The aircraft moves from the FAF toward the runway.")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            faf = num("FAF altitude (ft)", "w_cdfa_faf", 500, 8000, 50)
            thr = num("Runway threshold elevation (ft)", "w_cdfa_thr", 0, 6000, 10)
            mda = num("MDA (ft)", "w_cdfa_mda", 200, 7000, 10)
        with c2:
            vda = float(st.slider("VDA (degrees)", min_value=P.VDA_MIN, max_value=P.VDA_MAX, step=0.01, key="w_cdfa_vda"))
            gs = num("Final-approach ground speed (kt)", "w_cdfa_gs", 60, 200, 5)
            buf = num("DDA buffer above MDA (ft)", "w_cdfa_buf", 0, 200, 10)
        with c3:
            dive = num("Dive-and-drive descent rate to MDA (ft/min)", "w_cdfa_dive", 500, 3000, 100)
            ter = st.checkbox("Include a simple terrain ridge", key="w_cdfa_ter")
            low = num("Low-height alert (ft above terrain)", "w_cdfa_low", 50, 1000, 10,
                      help="Guide 3.2 mentions dive-and-drive level flight sometimes as low as 250 ft above the ground.")
        if ter:
            t1, t2, t3 = st.columns(3)
            with t1:
                peak = num("Ridge peak elevation (ft)", "w_cdfa_peak", 0, 6000, 50)
            with t2:
                xpeak = num("Ridge distance from threshold (NM)", "w_cdfa_xpeak", 0.0, 15.0, 0.5, "%.1f")
            with t3:
                hw = num("Ridge half-width (NM)", "w_cdfa_hw", 0.3, 5.0, 0.1, "%.1f")
    reset_button("cdfa", CDFA_DEF)

    if ter and peak < thr:
        st.error("Ridge peak elevation must not be lower than the threshold elevation.")
        return
    if show_errors(P.validate_cdfa(float(faf), float(thr), float(mda), vda, float(gs), float(buf), float(dive))):
        return
    g = P.cdfa_geometry(float(faf), float(thr), float(mda), vda, float(gs), float(buf), float(dive))
    cdfa, dd = P.cdfa_profiles(g, float(faf), float(thr), float(mda), float(gs))
    terrain = (lambda x: P.terrain_profile(x, thr, peak, xpeak, hw)) if ter else (lambda x: P.terrain_profile(x, thr, thr, 0.0, 1.0))
    zones = P.cfit_zones(g["x_dive_end"], g["d_mda"], float(mda), terrain, float(low))

    def min_agl(df):
        m = df.to_go_nm >= g["d_dda"]
        return float(np.min(df.alt_ft[m] - terrain(df.to_go_nm[m])))
    zone_len = sum(abs(a - b) for a, b in zones)
    too_steep = g["rod"] > P.STABILIZED_MAX_FPM
    st.markdown(metric_grid([
        metric_card("CDFA descent rate", f"{g['rod']:,.0f}", "ft/min", "warn" if too_steep else "ok",
                    "Exceeds the 1,000 fpm stabilized criterion" if too_steep else "Under 1,000 fpm (guide 3.3)"),
        metric_card("Derived Decision Altitude", f"{g['dda']:,.0f}", "ft", None, "MDA plus buffer"),
        metric_card("FAF to threshold", f"{g['d_faf']:.1f}", "NM", None, f"{g['d_faf'] / gs * 60:.1f} min at this ground speed"),
        metric_card("Dive-and-drive level segment", f"{g['level_nm']:.1f}", "NM", "warn", f"{g['level_min']:.1f} min level at MDA; dive rate {dive:,.0f} ft/min"),
        metric_card("CFIT risk zone", f"{zone_len:.1f}" if zones else "None", "NM" if zones else "",
                    "warn" if zones else "ok", f"Below {low:.0f} ft above terrain while level"),
        metric_card("Lowest height above terrain (to DDA)", f"{min_agl(dd):,.0f}", "ft", None, f"Dive and drive. CDFA: {min_agl(cdfa):,.0f} ft"),
    ]), unsafe_allow_html=True)
    if too_steep:
        st.warning(f"The CDFA descent rate is {g['rod']:,.0f} ft/min, above the 1,000 fpm stabilized-approach criterion in the guide. "
                   "Lower the ground speed or the VDA.")
    show_fig(charts.cdfa_figure(cdfa, dd, g, float(faf), float(thr), float(mda), terrain, zones, is_pres()), "fig_cdfa")
    out = pd.concat([cdfa.assign(profile="CDFA"), dd.assign(profile="Dive and drive")])
    csv_button(out, "cdfa_profiles.csv", "cdfa")
    formulas_box("cdfa", """
- Path gradient = tan(VDA) x 6,076 ft/NM. Distance from FAF to threshold = (FAF altitude - threshold elevation) / gradient.
- CDFA descent rate (ft/min) = ground speed (kt) x 101.27 x tan(VDA), i.e. about 5 x ground speed for 3 degrees.
- DDA = MDA + buffer. The CDFA line is dotted below the DDA because the pilot lands visually or goes around there.
- Dive and drive: descend at the entered rate from the FAF to the MDA, fly level, then continue down the same VDA path from the point where that path crosses the MDA.
- Terrain: flat at the threshold elevation plus one triangular ridge. CFIT risk zone = part of the level segment lower than the alert height above terrain.
- Ignored: obstacle clearance rules, temperature and pressure errors, aircraft performance, and the threshold crossing height.""")


# ----------------------------------------------------------------------------
# D) SID / STAR crossing scenario
# ----------------------------------------------------------------------------
SX_DEF = {"w_sx_dx0": 0.0, "w_sx_dy0": 0.0, "w_sx_dx1": 30.0, "w_sx_dy1": 30.0, "w_sx_da0": 0, "w_sx_da1": 15000,
          "w_sx_dr": 1800, "w_sx_ds": 250,
          "w_sx_ax0": 40.0, "w_sx_ay0": 0.0, "w_sx_ax1": 0.0, "w_sx_ay1": 30.0, "w_sx_aa0": 20000, "w_sx_aa1": 3000,
          "w_sx_ar": 1500, "w_sx_as": 280,
          "w_sx_off": 0.0, "w_sx_minh": 3.0, "w_sx_minv": 1000,
          "w_sx_apply": False, "w_sx_which": "Departure (SID)", "w_sx_altmode": "Auto-suggest", "w_sx_manual": 9000,
          "w_sx_release": 5.0, "w_sx_fclimb": P.DEFAULT_CLIMB_LEVEL_KG_PER_MIN, "w_sx_fdesc": round(P.GUIDE_KG_PER_MIN, 1)}


def sim_sidstar() -> None:
    init(SX_DEF)
    st.markdown("### SID / STAR crossing scenario")
    st.caption("Separation is considered lost only when BOTH the horizontal and vertical minima are infringed at the same time.")
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Departure (SID)**")
            a, b = st.columns(2)
            with a:
                num("Start X (NM)", "w_sx_dx0", -100.0, 100.0, 1.0, "%.1f")
                num("End X (NM)", "w_sx_dx1", -100.0, 100.0, 1.0, "%.1f")
            with b:
                num("Start Y (NM)", "w_sx_dy0", -100.0, 100.0, 1.0, "%.1f")
                num("End Y (NM)", "w_sx_dy1", -100.0, 100.0, 1.0, "%.1f")
            num("Start altitude (ft)", "w_sx_da0", 0, 30000, 500)
            num("Target altitude (ft)", "w_sx_da1", 1000, 45000, 500)
            num("Climb rate (ft/min)", "w_sx_dr", 300, 6000, 100)
            num("Ground speed (kt)", "w_sx_ds", 120, 500, 5)
        with c2:
            st.markdown("**Arrival (STAR)**")
            a, b = st.columns(2)
            with a:
                num("Start X (NM)", "w_sx_ax0", -100.0, 100.0, 1.0, "%.1f")
                num("End X (NM)", "w_sx_ax1", -100.0, 100.0, 1.0, "%.1f")
            with b:
                num("Start Y (NM)", "w_sx_ay0", -100.0, 100.0, 1.0, "%.1f")
                num("End Y (NM)", "w_sx_ay1", -100.0, 100.0, 1.0, "%.1f")
            num("Start altitude (ft)", "w_sx_aa0", 1000, 45000, 500)
            num("Target altitude (ft)", "w_sx_aa1", 0, 30000, 500)
            num("Descent rate (ft/min)", "w_sx_ar", 300, 6000, 100)
            num("Ground speed (kt)", "w_sx_as", 120, 500, 5)
        with c3:
            st.markdown("**Timing and separation**")
            st.slider("Departure start time offset (min)", min_value=-10.0, max_value=10.0, step=0.5, key="w_sx_off",
                      help="Positive: the departure starts later than the arrival. Negative: earlier.")
            num("Minimum horizontal separation (NM)", "w_sx_minh", 1.0, 10.0, 0.5, "%.1f")
            num("Minimum vertical separation (ft)", "w_sx_minv", 500, 3000, 100)
            with st.expander("Level-off fuel factors (editable)"):
                num("Level in climb (kg/min)", "w_sx_fclimb", 1.0, 200.0, 1.0, "%.1f")
                num("Level in descent (kg/min)", "w_sx_fdesc", 1.0, 100.0, 0.1, "%.1f")
    reset_button("sx", SX_DEF)

    g = st.session_state
    errs = []
    d0, d1 = (g.w_sx_dx0, g.w_sx_dy0), (g.w_sx_dx1, g.w_sx_dy1)
    a0, a1 = (g.w_sx_ax0, g.w_sx_ay0), (g.w_sx_ax1, g.w_sx_ay1)
    if d0 == d1:
        errs.append("The SID start and end points must be different.")
    if a0 == a1:
        errs.append("The STAR start and end points must be different.")
    if g.w_sx_da1 <= g.w_sx_da0:
        errs.append("The departure target altitude must be above its start altitude.")
    if g.w_sx_aa1 >= g.w_sx_aa0:
        errs.append("The arrival target altitude must be below its start altitude.")
    if show_errors(errs):
        return
    off = float(g.w_sx_off)
    dep = P.make_aircraft("DEP", d0, d1, g.w_sx_ds, max(0.0, off), g.w_sx_da0, g.w_sx_da1, g.w_sx_dr)
    arr = P.make_aircraft("ARR", a0, a1, g.w_sx_as, max(0.0, -off), g.w_sx_aa0, g.w_sx_aa1, g.w_sx_ar)
    t = P.sim_time_grid(dep, arr)
    min_h, min_v = float(g.w_sx_minh), float(g.w_sx_minv)
    base_viol = P.pair_metrics(P.aircraft_state(dep, t), P.aircraft_state(arr, t), min_h, min_v)[2].any()
    cross = P.seg_intersection(d0, d1, a0, a1)

    # --- controller level-off options (computed for both aircraft so the trade-off is visible)
    opts = {}
    if cross is not None and base_viol:
        for which in ("dep", "arr"):
            opts[which] = P.best_level_off(which, dep, arr, t, min_h, min_v, cross[0], cross[1], float(g.w_sx_release))
    fuel = {"dep": float(g.w_sx_fclimb), "arr": float(g.w_sx_fdesc)}

    st.markdown("#### Controller action")
    if cross is None:
        st.info("The two routes do not cross, so no level-off point can be defined. Move a route so the lines intersect.")
    elif not base_viol:
        st.markdown(callout("<b>No separation loss</b> with the current numbers. Change the start-time offset or the speeds to create a conflict.", "ok"),
                    unsafe_allow_html=True)
    else:
        st.markdown(callout("<b>Separation lost</b> with no controller action. Enable the level-off below and compare the cost.", "alert"),
                    unsafe_allow_html=True)
    dep2, arr2, applied = dep, arr, None
    if cross is not None:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.checkbox("Apply controller level-off", key="w_sx_apply")
        if g.w_sx_apply:
            with c2:
                st.radio("Level off this aircraft", ["Departure (SID)", "Arrival (STAR)"], key="w_sx_which")
            with c3:
                st.radio("Level-off altitude", ["Auto-suggest", "Manual"], key="w_sx_altmode")
                if g.w_sx_altmode == "Manual":
                    num("Manual level-off altitude (ft)", "w_sx_manual", 500, 45000, 100)
            with c4:
                num("Hold until N NM past the crossing", "w_sx_release", 0.0, 30.0, 1.0, "%.1f")
            which = "dep" if g.w_sx_which.startswith("Dep") else "arr"
            base_ac, s_cross = (dep, cross[0]) if which == "dep" else (arr, cross[1])
            if g.w_sx_altmode == "Auto-suggest":
                mod = opts.get(which) if base_viol else None
                if mod is None:
                    st.warning("No single level-off altitude removes the loss for this aircraft (or there is no loss). Try the other aircraft or enter an altitude manually.")
                    mod = base_ac
            else:
                mod = P.apply_level_off(base_ac, float(g.w_sx_manual), s_cross, float(g.w_sx_release))
                if mod is base_ac:
                    st.warning("The manual level-off altitude must lie between the aircraft's start and target altitudes.")
            if which == "dep":
                dep2 = mod
            else:
                arr2 = mod
            applied = (which, mod)

    h, v, viol = P.pair_metrics(P.aircraft_state(dep2, t), P.aircraft_state(arr2, t), min_h, min_v)
    i = int(np.nanargmin(h)) if np.isfinite(h).any() else 0
    viol_s = float(viol.sum() * (t[1] - t[0]) * 60.0)
    cards = [
        metric_card("Closest horizontal approach", f"{np.nanmin(h):.1f}" if np.isfinite(h).any() else "n/a", "NM",
                    "conflict" if viol.any() else "ok", f"At t = {t[i]:.1f} min"),
        metric_card("Vertical separation at that moment", f"{v[i]:,.0f}" if np.isfinite(v[i]) else "n/a", "ft", None,
                    f"Minimum required: {min_v:,.0f} ft"),
        metric_card("Time below both minima", f"{viol_s:.0f}", "s", "conflict" if viol.any() else "ok",
                    "Separation lost" if viol.any() else "Separation maintained"),
    ]
    if applied and applied[1]["level_alt"] is not None:
        which, mod = applied
        label = "CCO" if which == "dep" else "CDO"
        cards.append(metric_card(f"{label} cost of the level-off", f"{mod['hold_min'] * fuel[which]:.0f}", "kg",
                                 "warn", f"{mod['hold_min']:.1f} min level at {mod['level_alt']:,.0f} ft (educational approximation)"))
    st.markdown(metric_grid(cards), unsafe_allow_html=True)

    if opts:
        rows = []
        for which, nm, eff in (("dep", "Departure (SID)", "CCO"), ("arr", "Arrival (STAR)", "CDO")):
            m = opts[which]
            rows.append({"Level off": nm, "Technique affected": eff,
                         "Level-off altitude (ft)": f"{m['level_alt']:,.0f}" if m else "none works",
                         "Time level (min)": f"{m['hold_min']:.1f}" if m else "-",
                         "Extra fuel (kg)": f"{m['hold_min'] * fuel[which]:.0f}" if m else "-"})
        st.markdown("**Trade-off: which aircraft should level off?**")
        show_table(pd.DataFrame(rows))
        if opts["dep"] and opts["arr"]:
            cd, ca = opts["dep"]["hold_min"] * fuel["dep"], opts["arr"]["hold_min"] * fuel["arr"]
            cheaper = "arrival (CDO)" if ca < cd else "departure (CCO)"
            st.markdown(callout(f"With these fuel factors, levelling the <b>{cheaper}</b> costs less fuel ({min(cd, ca):.0f} kg vs {max(cd, ca):.0f} kg). "
                                "This follows the guide's principle: a forced level segment in climb burns significantly more fuel than an equivalent one in descent "
                                "(section 8.2). Controllers must still weigh safety, throughput and workload.", "info"), unsafe_allow_html=True)

    ghost = {}
    if applied and applied[1]["level_alt"] is not None:
        orig = dep if applied[0] == "dep" else arr
        ghost = {orig["name"]: P.aircraft_state(orig, t)[2]}
    tracks = {"DEP": P.aircraft_state(dep2, t), "ARR": P.aircraft_state(arr2, t)}
    pts = [(float(cross[2][0]), float(cross[2][1]), "Crossing point")] if cross is not None else []
    show_fig(charts.traffic_figure(t, tracks, {("DEP", "ARR"): (h, v, viol)}, min_h, min_v, is_pres(), pts, ghost,
                                   "SID/STAR crossing: plan view and altitude vs time"), "fig_sx")
    out = pd.DataFrame({"time_min": t, "dep_x_nm": tracks["DEP"][0], "dep_y_nm": tracks["DEP"][1], "dep_alt_ft": tracks["DEP"][2],
                        "arr_x_nm": tracks["ARR"][0], "arr_y_nm": tracks["ARR"][1], "arr_alt_ft": tracks["ARR"][2],
                        "horizontal_nm": h, "vertical_ft": v, "separation_lost": viol})
    csv_button(out, "sid_star_crossing.csv", "sx")
    formulas_box("sx", """
- Each aircraft flies a straight line from its start to its end point at constant ground speed; altitude changes at a constant rate until the target altitude. An aircraft disappears when it leaves its route.
- Horizontal distance = straight-line distance between the two positions. Vertical distance = absolute altitude difference.
- Separation is lost only when horizontal distance < minimum AND vertical distance < minimum at the same moment (defaults 3 NM and 1,000 ft).
- Level-off: the chosen aircraft climbs/descends to the level-off altitude, holds it until it is N NM past the crossing point, then continues. "Auto-suggest" scans altitudes in 100 ft steps and picks the shortest level segment that removes the separation loss.
- Extra fuel = time level (min) x the editable fuel factor for climb or descent. These factors are assumptions; the guide gives only the qualitative rule that a level segment in climb costs significantly more than one in descent.
- Ignored: turns, wind, speed changes, aircraft type, radar and communication delays.""")


# ----------------------------------------------------------------------------
# E) Multi-aircraft mode
# ----------------------------------------------------------------------------
MULTI_DEF = {"w_multi_T": 12.0, "w_multi_minh": 3.0, "w_multi_minv": 1000}


def _reset_multi() -> None:
    _reset(MULTI_DEF)
    st.session_state["multi_df"] = P.default_multi_table()
    st.session_state["multi_ver"] = st.session_state.get("multi_ver", 0) + 1


def sim_multi() -> None:
    init(MULTI_DEF)
    st.session_state.setdefault("multi_df", P.default_multi_table())
    st.session_state.setdefault("multi_ver", 0)
    st.markdown("### Multi-aircraft mode (bonus)")
    st.caption("Edit the table (3 to 6 aircraft). Heading 0 = north, 90 = east. Rows can be added or deleted.")
    cc = st.column_config
    config = {
        "Callsign": cc.TextColumn("Callsign", required=True),
        "Type": cc.SelectboxColumn("Type", options=["Departure", "Arrival"], required=True),
        "Start X (NM)": cc.NumberColumn(format="%.1f"), "Start Y (NM)": cc.NumberColumn(format="%.1f"),
        "Heading (deg)": cc.NumberColumn(min_value=0, max_value=360, format="%.0f"),
        "Speed (kt)": cc.NumberColumn(min_value=50, max_value=600, format="%.0f"),
        "Start alt (ft)": cc.NumberColumn(min_value=0, max_value=45000, format="%.0f"),
        "V/S (ft/min)": cc.NumberColumn(min_value=0, max_value=8000, format="%.0f", help="Positive number; the type decides climb or descent."),
        "Target alt (ft)": cc.NumberColumn(min_value=0, max_value=45000, format="%.0f"),
        "Start offset (min)": cc.NumberColumn(min_value=0, max_value=30, format="%.1f"),
    }
    kwargs = dict(key=f"multi_editor_{st.session_state['multi_ver']}", num_rows="dynamic", column_config=config, hide_index=True)
    try:
        edited = st.data_editor(st.session_state["multi_df"], width="stretch", **kwargs)
    except Exception:
        edited = st.data_editor(st.session_state["multi_df"], use_container_width=True, **kwargs)
    st.session_state["multi_df"] = edited           # keep edits when switching pages
    c1, c2, c3 = st.columns(3)
    with c1:
        num("Simulation length (min)", "w_multi_T", 2.0, 30.0, 1.0, "%.0f")
    with c2:
        num("Minimum horizontal separation (NM)", "w_multi_minh", 1.0, 10.0, 0.5, "%.1f")
    with c3:
        num("Minimum vertical separation (ft)", "w_multi_minv", 500, 3000, 100)
    with st.container(key="sec-reset-multi"):
        st.button("Reset to defaults", key="sec-resetbtn-multi", on_click=_reset_multi)

    df = edited.reset_index(drop=True).copy()
    if show_errors(P.validate_multi(df)):
        return
    df["Callsign"] = df["Callsign"].astype(str).str.strip()
    t = np.arange(0.0, float(st.session_state["w_multi_T"]) + 0.05, 0.05)
    states = P.multi_states(df, t)
    min_h, min_v = float(st.session_state["w_multi_minh"]), float(st.session_state["w_multi_minv"])
    pairs, episodes = P.multi_conflicts(states, t, min_h, min_v)
    if episodes:
        names = ", ".join(sorted({e["Pair"] for e in episodes}))
        st.markdown(callout(f"<b>ALERT: separation violated</b> for {names}. See the red markers and links on the chart.", "alert"),
                    unsafe_allow_html=True)
        show_table(pd.DataFrame(episodes).rename(columns={"From_min": "From (min)", "To_min": "To (min)",
                                                          "Min_horizontal_NM": "Min horizontal (NM)", "Min_vertical_ft": "Min vertical (ft)"}))
    else:
        st.markdown(callout("<b>No separation loss</b> between any pair with these inputs.", "ok"), unsafe_allow_html=True)
    show_fig(charts.traffic_figure(t, states, pairs, min_h, min_v, is_pres(), title="All aircraft: plan view and altitude vs time"), "fig_multi")
    rows = []
    for name, (x, y, alt) in states.items():
        rows.append(pd.DataFrame({"callsign": name, "time_min": t, "x_nm": x, "y_nm": y, "alt_ft": alt}))
    csv_button(pd.concat(rows), "multi_aircraft_tracks.csv", "multi")
    formulas_box("multi", """
- Each aircraft flies a straight line from its start position on its heading at constant ground speed (x = x0 + sin(heading) x distance, y = y0 + cos(heading) x distance).
- Altitude changes at the entered rate from the start altitude toward the target altitude, then holds.
- Every pair is checked at every 3-second step. A violation needs horizontal distance < minimum AND vertical distance < minimum at the same moment.
- Ignored: turns, wind, acceleration, aircraft type and any controller action. This view only shows where separation would be lost.""")
