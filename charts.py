"""Plotly figure builders (no Streamlit dependency). One shared dark 'radar console' template."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from theme import AMBER, CYAN, FONT_STACK, GRID, GREEN, MONO_STACK, MUTED, RED, TEXT, AIRCRAFT_COLORS

PLOT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    # The camera icon in the chart toolbar saves a PNG (works offline, no extra packages).
    "toImageButtonOptions": {"format": "png", "scale": 2, "filename": "atc_lab_chart"},
}
AXIS_LINE = "#2a3d62"


def _fs(pres: bool) -> int:
    return 18 if pres else 13


def style(fig, title: str, pres: bool, height: int = 540, bottom: int = 150):
    """Apply the shared template (dark background, readable fonts, hover style)."""
    fs = _fs(pres)
    fig.update_layout(
        title=dict(text=title, x=0.01, y=0.985, xanchor="left", yanchor="top", font=dict(size=fs + 4, color="#ffffff")),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,15,30,.85)",
        font=dict(family=FONT_STACK, color=TEXT, size=fs),
        height=height + (60 if pres else 0),
        margin=dict(l=76, r=28, t=96, b=bottom),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1.0,
                    bgcolor="rgba(0,0,0,0)", font=dict(size=fs - 1, color=TEXT)),
        hoverlabel=dict(bgcolor="#0f1b33", bordercolor=GREEN, font=dict(family=MONO_STACK, size=fs - 1, color=TEXT)),
    )
    axis = dict(gridcolor="rgba(120,160,255,.10)", griddash="dot", zerolinecolor=AXIS_LINE, linecolor=AXIS_LINE, showline=True, ticks="outside", tickcolor=AXIS_LINE,
                tickfont=dict(size=fs - 1), title_font=dict(size=fs))
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    return fig


def attach_animation(fig, n_static: int, frames: list, labels: list, frame_ms: int, pres: bool):
    """Play/Pause buttons + time slider. frames[i] = list of traces replacing traces n_static.. ."""
    fs = _fs(pres)
    idx = list(range(n_static, n_static + len(frames[0])))
    fig.frames = [go.Frame(data=f, traces=idx, name=str(i)) for i, f in enumerate(frames)]
    no_redraw = dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))
    fig.update_layout(
        updatemenus=[dict(
            type="buttons", direction="left", x=0.0, y=-0.19, xanchor="left", yanchor="top", showactive=False,
            bgcolor="#12233f", bordercolor=GREEN, font=dict(color=GREEN, size=fs), pad=dict(r=6, t=2),
            buttons=[
                dict(label="▶  Play", method="animate",
                     args=[None, dict(frame=dict(duration=frame_ms, redraw=False), transition=dict(duration=0),
                                      fromcurrent=True, mode="immediate")]),
                dict(label="⏸  Pause", method="animate", args=[[None], no_redraw]),
            ])],
        sliders=[dict(
            active=0, x=0.2, y=-0.19, len=0.8, xanchor="left", yanchor="top", pad=dict(t=0, b=0),
            currentvalue=dict(prefix="Time: ", font=dict(color=GREEN, size=fs, family=MONO_STACK)),
            font=dict(color="rgba(0,0,0,0)", size=1),        # hide the dense tick labels
            tickcolor="rgba(0,0,0,0)", bgcolor=GRID, bordercolor=AXIS_LINE, activebgcolor=GREEN,
            steps=[dict(method="animate", label=lab, args=[[str(i)], no_redraw]) for i, lab in enumerate(labels)],
        )])
    return fig


def _marker(x, y, color, text=None, size=16, symbol="diamond"):
    return go.Scatter(x=[x], y=[y], mode="markers+text" if text else "markers",
                      text=[text] if text else None, textposition="top center", textfont=dict(color=color),
                      marker=dict(size=size, color=color, symbol=symbol, line=dict(color="#ffffff", width=1.5)),
                      showlegend=False, hoverinfo="skip")


def flat_segments(df, xcol):
    """Level-flight pieces of a profile (consecutive samples with identical altitude)."""
    x, y = df[xcol].to_numpy(), df["alt_ft"].to_numpy()
    flat = np.isclose(np.diff(y), 0.0)
    segs, i = [], 0
    while i < len(flat):
        if flat[i]:
            j = i
            while j < len(flat) and flat[j]:
                j += 1
            segs.append((x[i:j + 1], y[i:j + 1]))
            i = j
        else:
            i += 1
    return segs


def _line(df, xcol, name, color, width=4, dash=None, tip=""):
    return go.Scatter(x=df[xcol], y=df["alt_ft"], mode="lines", name=name,
                      line=dict(color=color, width=width, dash=dash),
                      hovertemplate=f"{tip}<br>%{{x:.1f}} NM, %{{y:,.0f}} ft<extra></extra>")


def _level_traces(fig, df, xcol, label="ATC level-off"):
    for k, (xs, ys) in enumerate(flat_segments(df, xcol)):
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=label, legendgroup="lvl", showlegend=(k == 0),
                                 line=dict(color=RED, width=8), hovertemplate="Level at %{y:,.0f} ft<extra></extra>"))


def _two_marker_frames(a, b, xcol, ycol, ts, col_a, col_b, text_a=None, text_b=None):
    frames, labels = [], []
    for t in ts:
        pa = (np.interp(t, a["time_min"], a[xcol]), np.interp(t, a["time_min"], a[ycol]))
        pb = (np.interp(t, b["time_min"], b[xcol]), np.interp(t, b["time_min"], b[ycol]))
        frames.append([_marker(*pa, col_a, text_a), _marker(*pb, col_b, text_b, symbol="diamond-open")])
        labels.append(f"{t:.1f} min")
    return frames, labels


# ----------------------------------------------------------------------------
# A) CCO
# ----------------------------------------------------------------------------
def cco_figure(cont, step, cruise_alt, pres, n_frames=90):
    fig = go.Figure()
    fig.add_trace(_line(step, "dist_nm", "Stepped climb", AMBER, 3, "dash", "Stepped climb"))
    fig.add_trace(_line(cont, "dist_nm", "Continuous climb (CCO)", GREEN, 4, None, "CCO"))
    _level_traces(fig, step, "dist_nm")
    for df, col, nm in ((cont, GREEN, "ToC (CCO)"), (step, AMBER, "ToC (stepped)")):
        fig.add_trace(go.Scatter(x=[df.dist_nm.iloc[-1]], y=[cruise_alt], mode="markers", name=nm, showlegend=False,
                                 marker=dict(size=11, color=col, symbol="star", line=dict(color="#fff", width=1)),
                                 hovertemplate=nm + "<br>%{x:.1f} NM<extra></extra>"))
    fig.add_hline(y=cruise_alt, line=dict(color=MUTED, dash="dot", width=1),
                  annotation_text=f"Initial cruise FL{cruise_alt / 100:.0f}", annotation_position="top left",
                  annotation_font=dict(color=MUTED))
    n_static = len(fig.data)
    T = max(cont.time_min.max(), step.time_min.max())
    ts = np.linspace(0, T, n_frames)
    frames, labels = _two_marker_frames(cont, step, "dist_nm", "alt_ft", ts, GREEN, AMBER)
    fig.add_traces(frames[0])
    style(fig, "CCO side view: continuous vs stepped climb", pres)
    fig.update_xaxes(title="Horizontal distance flown (NM)")
    fig.update_yaxes(title="Altitude (ft)", tickformat=",", range=[0, cruise_alt * 1.12])
    return attach_animation(fig, n_static, frames, labels, 70, pres)


# ----------------------------------------------------------------------------
# B) CDO
# ----------------------------------------------------------------------------
def cdo_figure(cdo, step, start_alt, faf_alt, d_desc, pres, n_frames=90):
    fig = go.Figure()
    fig.add_trace(_line(step, "to_go_nm", "Step-down arrival", AMBER, 3, "dash", "Step-down"))
    fig.add_trace(_line(cdo, "to_go_nm", "CDO (idle descent)", GREEN, 4, None, "CDO"))
    _level_traces(fig, step, "to_go_nm")
    fig.add_hline(y=faf_alt, line=dict(color=CYAN, dash="dot", width=1), annotation_text=f"FAF {faf_alt:,.0f} ft",
                  annotation_position="bottom right", annotation_font=dict(color=CYAN))
    fig.add_vline(x=d_desc, line=dict(color=GREEN, dash="dot", width=1), annotation_text="TOD (CDO)",
                  annotation_position="top", annotation_font=dict(color=GREEN))
    n_static = len(fig.data)
    ts = np.linspace(0, cdo.time_min.max(), n_frames)
    frames, labels = _two_marker_frames(cdo, step, "to_go_nm", "alt_ft", ts, GREEN, AMBER)
    fig.add_traces(frames[0])
    style(fig, "CDO side view: continuous descent vs step-down", pres)
    fig.update_xaxes(title="Distance to FAF (NM)", autorange="reversed")
    fig.update_yaxes(title="Altitude (ft)", tickformat=",", range=[max(0, faf_alt - 1500), start_alt * 1.08 + 500])
    return attach_animation(fig, n_static, frames, labels, 70, pres)


def dtg_figure(dtg, elev, current_alt, path_fn, pres):
    xs = np.linspace(0, max(60.0, dtg * 1.25), 120)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[path_fn(x) for x in xs], mode="lines", name="3-degree path",
                             line=dict(color=GREEN, width=4), hovertemplate="%{x:.1f} NM to go, %{y:,.0f} ft<extra></extra>"))
    fig.add_trace(go.Scatter(x=[dtg], y=[path_fn(dtg)], mode="markers+text", name="Suggested altitude",
                             text=[f"{path_fn(dtg):,.0f} ft"], textposition="bottom right",
                             marker=dict(size=13, color=GREEN, symbol="diamond", line=dict(color="#fff", width=1.5))))
    if current_alt is not None:
        fig.add_trace(go.Scatter(x=[dtg], y=[current_alt], mode="markers+text", name="Current altitude",
                                 text=[f"{current_alt:,.0f} ft"], textposition="top right",
                                 marker=dict(size=13, color=AMBER, symbol="triangle-up", line=dict(color="#fff", width=1.5))))
    style(fig, "Distance-to-Go: suggested altitude on a 3-degree path", pres, height=420, bottom=80)
    fig.update_xaxes(title="Distance to go to the airport (NM)", autorange="reversed")
    fig.update_yaxes(title="Altitude (ft)", tickformat=",")
    return fig


# ----------------------------------------------------------------------------
# C) CDFA
# ----------------------------------------------------------------------------
def cdfa_figure(cdfa, dd, g, faf_alt, thr_elev, mda, terrain_fn, zones, pres, n_frames=90):
    fig = go.Figure()
    xs = np.linspace(g["d_faf"] + 1.0, -0.6, 400)
    ter = terrain_fn(xs)
    fig.add_trace(go.Scatter(x=xs, y=ter, mode="lines", name="Terrain", fill="tozeroy", fillcolor="rgba(120,140,170,.28)",
                             line=dict(color="#7f93b5", width=1.5), hovertemplate="Terrain %{y:,.0f} ft<extra></extra>"))
    fig.add_trace(_line(dd, "to_go_nm", "Dive and drive", AMBER, 3, "dash", "Dive and drive"))
    above = cdfa[cdfa.alt_ft >= g["dda"]]
    below = cdfa[cdfa.alt_ft <= g["dda"]]
    fig.add_trace(_line(above, "to_go_nm", "CDFA (constant VDA)", GREEN, 4, None, "CDFA"))
    fig.add_trace(go.Scatter(x=below.to_go_nm, y=below.alt_ft, mode="lines", name="Below DDA (visual segment)",
                             line=dict(color=GREEN, width=2, dash="dot"), hoverinfo="skip"))
    fig.add_hline(y=mda, line=dict(color=AMBER, dash="dot", width=1), annotation_text=f"MDA {mda:,.0f} ft",
                  annotation_position="top left", annotation_font=dict(color=AMBER))
    fig.add_hline(y=g["dda"], line=dict(color=CYAN, dash="dot", width=1), annotation_text=f"DDA {g['dda']:,.0f} ft",
                  annotation_position="bottom left", annotation_font=dict(color=CYAN))
    fig.add_vline(x=g["d_faf"], line=dict(color=MUTED, dash="dot", width=1), annotation_text="FAF",
                  annotation_position="top", annotation_font=dict(color=MUTED))
    for k, (xa, xb) in enumerate(zones):
        fig.add_vrect(x0=xa, x1=xb, fillcolor=RED, opacity=0.2, line_width=0, layer="below",
                      annotation_text="CFIT risk zone" if k == 0 else None, annotation_position="top",
                      annotation_font=dict(color=RED))
    fig.add_shape(type="rect", x0=0, x1=-0.5, y0=thr_elev - 25, y1=thr_elev, fillcolor=MUTED, line_width=0)
    fig.add_annotation(x=-0.25, y=thr_elev, text="RWY", showarrow=False, yshift=-22, font=dict(color=MUTED))
    n_static = len(fig.data)
    ts = np.linspace(0, cdfa.time_min.max(), n_frames)
    frames, labels = _two_marker_frames(cdfa, dd, "to_go_nm", "alt_ft", ts, GREEN, AMBER)
    fig.add_traces(frames[0])
    style(fig, "CDFA side view: constant slope vs dive and drive", pres)
    fig.update_xaxes(title="Distance to runway threshold (NM)", autorange="reversed")
    fig.update_yaxes(title="Altitude (ft)", tickformat=",", range=[max(0, thr_elev - 250), faf_alt * 1.08 + 100])
    return attach_animation(fig, n_static, frames, labels, 70, pres)


# ----------------------------------------------------------------------------
# D / E) Plan view + altitude-time view with animation (shared by SID/STAR and multi-aircraft)
# ----------------------------------------------------------------------------
def traffic_figure(t, tracks, pairs, min_h, min_v, pres, extra_points=None, ghost=None,
                   title="Plan view and altitude profile", n_frames=120):
    """tracks: name -> (x, y, alt) arrays (NaN when not visible); pairs: (a, b) -> (H, V, viol)."""
    names = list(tracks)
    colors = {n: AIRCRAFT_COLORS[i % len(AIRCRAFT_COLORS)] for i, n in enumerate(names)}
    fig = make_subplots(rows=1, cols=2, column_widths=[0.52, 0.48], horizontal_spacing=0.09,
                        subplot_titles=("Plan view (NM)", "Altitude vs time"))
    # static: full trajectories
    for n in names:
        x, y, alt = tracks[n]
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=n, legendgroup=n, line=dict(color=colors[n], width=2, dash="dot"),
                                 hovertemplate=n + "<br>%{x:.1f}, %{y:.1f} NM<extra></extra>"), row=1, col=1)
    for n in names:
        fig.add_trace(go.Scatter(x=t, y=tracks[n][2], mode="lines", name=n, legendgroup=n, showlegend=False,
                                 line=dict(color=colors[n], width=3),
                                 hovertemplate=n + "<br>%{x:.1f} min, %{y:,.0f} ft<extra></extra>"), row=1, col=2)
    for n, alt in (ghost or {}).items():
        fig.add_trace(go.Scatter(x=t, y=alt, mode="lines", name=f"{n} without level-off",
                                 line=dict(color=MUTED, width=2, dash="dash"),
                                 hovertemplate="Original profile<br>%{x:.1f} min, %{y:,.0f} ft<extra></extra>"), row=1, col=2)
    for (px, py, label) in (extra_points or []):
        fig.add_trace(go.Scatter(x=[px], y=[py], mode="markers+text", text=[label], textposition="bottom center",
                                 name=label, showlegend=False, textfont=dict(color=MUTED),
                                 marker=dict(size=10, color=MUTED, symbol="x")), row=1, col=1)
    conflict_pairs = [p for p, (_, _, viol) in pairs.items() if viol.any()]
    for p in conflict_pairs:
        viol = pairs[p][2]
        i = 0
        while i < len(viol):
            if viol[i]:
                j = i
                while j < len(viol) and viol[j]:
                    j += 1
                fig.add_vrect(x0=t[i], x1=t[j - 1], fillcolor=RED, opacity=0.22, line_width=0, layer="below", row=1, col=2)
                i = j
            else:
                i += 1
    n_static = len(fig.data)

    in_viol = {n: np.zeros(len(t), bool) for n in names}
    for (a, b), (_, _, viol) in pairs.items():
        in_viol[a] |= viol
        in_viol[b] |= viol
    amax = np.nanmax([np.nanmax(tracks[n][2]) for n in names])

    def frame_traces(i):
        out = []
        for n in names:                                   # plan markers
            x, y, _ = tracks[n]
            c = RED if in_viol[n][i] else colors[n]
            out.append(_marker(x[i], y[i], c, n if np.isfinite(x[i]) else None, size=15))
        for p in conflict_pairs:                          # separation links
            (a, b), (h, v, viol) = p, pairs[p]
            if viol[i]:
                xa, ya, xb, yb = tracks[a][0][i], tracks[a][1][i], tracks[b][0][i], tracks[b][1][i]
                out.append(go.Scatter(x=[xa, xb], y=[ya, yb], mode="lines+text", text=["", f"H {h[i]:.1f} NM / V {v[i]:,.0f} ft"],
                                      textposition="top right", textfont=dict(color=RED),
                                      line=dict(color=RED, width=3), showlegend=False, hoverinfo="skip"))
            else:
                out.append(go.Scatter(x=[None, None], y=[None, None], mode="lines", showlegend=False, hoverinfo="skip"))
        for n in names:                                   # altitude markers
            c = RED if in_viol[n][i] else colors[n]
            out.append(_marker(t[i], tracks[n][2][i], c, None, size=13))
        out.append(go.Scatter(x=[t[i], t[i]], y=[0, amax * 1.1], mode="lines", showlegend=False, hoverinfo="skip",
                              line=dict(color=GREEN, width=1, dash="dot")))
        return out

    idx = np.unique(np.linspace(0, len(t) - 1, n_frames).astype(int))
    frames = [frame_traces(i) for i in idx]
    labels = [f"{t[i]:.1f} min" for i in idx]
    plan_n = len(names) + len(conflict_pairs)
    for k, tr in enumerate(frames[0]):                    # initial state = first frame
        fig.add_trace(tr, row=1, col=1 if k < plan_n else 2)

    allx = np.concatenate([tracks[n][0][np.isfinite(tracks[n][0])] for n in names] +
                          [np.array([p[0] for p in (extra_points or [])])])
    ally = np.concatenate([tracks[n][1][np.isfinite(tracks[n][1])] for n in names] +
                          [np.array([p[1] for p in (extra_points or [])])])
    cx, cy = (allx.min() + allx.max()) / 2, (ally.min() + ally.max()) / 2
    half = max(allx.max() - allx.min(), ally.max() - ally.min(), 10.0) / 2 * 1.12
    style(fig, title, pres, height=560, bottom=160)
    fig.update_xaxes(title="East (NM)", range=[cx - half, cx + half], row=1, col=1)
    fig.update_yaxes(title="North (NM)", range=[cy - half, cy + half], scaleanchor="x", scaleratio=1, row=1, col=1)
    fig.update_xaxes(title="Time (min)", row=1, col=2)
    fig.update_yaxes(title="Altitude (ft)", tickformat=",", range=[0, amax * 1.1], row=1, col=2)
    for a in fig.layout.annotations:                      # subplot titles
        a.font = dict(size=_fs(pres) + 1, color=TEXT)
    return attach_animation(fig, n_static, frames, labels, 80, pres)


# ----------------------------------------------------------------------------
# Home / comparison
# ----------------------------------------------------------------------------
def concept_map(pres):
    """Schematic flight profile showing where CCO, CDO and CDFA sit, with CNS and ATM underneath."""
    fig = go.Figure()
    phases = [
        ("CCO: takeoff to Top of Climb", [0, 24], [8, 68], GREEN),
        ("Cruise", [24, 62], [68, 68], MUTED),
        ("CDO: ToD to FAF", [62, 88], [68, 22], CYAN),
        ("CDFA: FAF to threshold / DDA", [88, 100], [22, 4], AMBER),
    ]
    for name, xs, ys, col in phases:
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=name, line=dict(color=col, width=6 if col != MUTED else 3),
                                 hoverinfo="name"))
    for x, y, txt, col, anchor in ((8, 46, "CCO", GREEN, "right"), (75, 52, "CDO", CYAN, "left"), (95, 22, "CDFA", AMBER, "left")):
        fig.add_annotation(x=x, y=y, text=f"<b>{txt}</b>", showarrow=False, xanchor=anchor, font=dict(color=col, size=_fs(pres) + 4))
    fig.add_shape(type="rect", x0=0, x1=100, y0=-22, y1=-8, fillcolor="rgba(56,189,248,.12)", line=dict(color=CYAN, width=1))
    fig.add_annotation(x=50, y=-15, showarrow=False, font=dict(color=CYAN, size=_fs(pres)),
                       text="CNS: Communication (CPDLC) + Navigation (PBN, VNAV) + Surveillance (ADS-B, radar)")
    fig.add_shape(type="rect", x0=0, x1=100, y0=-42, y1=-28, fillcolor="rgba(57,255,136,.10)", line=dict(color=GREEN, width=1))
    fig.add_annotation(x=50, y=-35, showarrow=False, font=dict(color=GREEN, size=_fs(pres)),
                       text="ATM: Trajectory-Based Operations + AMAN / DMAN + cross-sector coordination")
    style(fig, "Where each technique sits (schematic, not to scale)", pres, height=430, bottom=30)
    fig.update_xaxes(visible=False, range=[-2, 102], showgrid=False)
    fig.update_yaxes(visible=False, range=[-46, 78], showgrid=False)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, xanchor="left"))
    return fig


BENEFIT_DIMS = ["Fuel and CO2 savings", "Noise mitigation", "Workload reduction", "CFIT risk elimination",
                "Predictable profile for ATC"]
BENEFIT_CITED = {   # 1 = explicitly cited in the guide for that operation, 0 = not cited
    "CCO": [1, 1, 1, 0, 0],
    "CDO": [1, 1, 1, 0, 0],
    "CDFA": [0, 0, 1, 1, 1],
}
_CMP_COLORS = {"CCO": GREEN, "CDO": CYAN, "CDFA": AMBER}


def comparison_figure(kind: str, pres: bool):
    fig = go.Figure()
    for op, vals in BENEFIT_CITED.items():
        col = _CMP_COLORS[op]
        if kind == "Radar":
            fig.add_trace(go.Scatterpolar(r=vals + vals[:1], theta=BENEFIT_DIMS + BENEFIT_DIMS[:1], name=op, fill="toself",
                                          line=dict(color=col, width=3), opacity=0.55))
        else:
            fig.add_trace(go.Bar(x=BENEFIT_DIMS, y=vals, name=op, marker_color=col))
    style(fig, "Benefits explicitly cited in the guide (1 = cited, 0 = not cited)", pres, height=500, bottom=60)
    if kind == "Radar":
        fig.update_layout(polar=dict(bgcolor="#0c1424", radialaxis=dict(range=[0, 1], tickvals=[0, 1], gridcolor=GRID, tickfont=dict(size=_fs(pres))),
                                     angularaxis=dict(gridcolor=GRID, tickfont=dict(size=_fs(pres)))))
    else:
        fig.update_layout(barmode="group")
        fig.update_yaxes(title="Cited in guide (1 = yes)", range=[0, 1.2], tickvals=[0, 1])
        fig.update_xaxes(title="Benefit dimension")
    return fig
