"""Static content pages (home, technique pages, comparison, CNS/ATM, challenges, quiz)."""
from __future__ import annotations

import streamlit as st

import charts
import content as C
import sims
from theme import bullets, callout, card, hero, metric_card, metric_grid


def page_header(title: str, sub: str = "") -> None:
    st.markdown(f'<div class="page-title">{title}</div><div class="page-sub">{sub}</div>', unsafe_allow_html=True)


def _ref_html(title, publisher, url, tag):
    link = (f'<a href="{url}" target="_blank" rel="noopener noreferrer">Open source &#8599;</a>' if url
            else '<span class="refnone">No link provided</span>')
    return (f'<div class="ref-card"><span class="ref-tag">{tag}</span><div class="ref-title">{title}</div>'
            f'<div class="ref-pub">{publisher}</div>{link}</div>')


# ----------------------------------------------------------------------------
def home() -> None:
    st.markdown(hero(), unsafe_allow_html=True)
    st.markdown("## Lesson objectives")
    st.markdown(card("By the end of this class you can", "<ol>" + "".join(f"<li>{o}</li>" for o in C.OBJECTIVES) + "</ol>", "g"),
                unsafe_allow_html=True)
    st.markdown("## How CCO, CDO and CDFA relate")
    sims.show_fig(charts.concept_map(sims.is_pres()), "fig_concept")
    st.markdown("## Feature comparison at a glance")
    cols = st.columns(3)
    for col, (name, tone, text) in zip(cols, C.SUMMARY_CARDS):
        idx = {"CCO": 1, "CDO": 2, "CDFA": 3}[name]
        rows = {r[0]: r[idx] for r in C.MATRIX}
        body = (f"<p>{text}</p>" + bullets([f"<b>Goal:</b> {rows['Primary goal']}", f"<b>Replaces:</b> {rows['Method replaced']}",
                                            f"<b>Key reference:</b> {rows['Critical reference']}"]))
        with col:
            st.markdown(card(name, body, tone), unsafe_allow_html=True)
    st.caption("The full matrix is on the Comparison page.")
    st.markdown("## Why it matters")
    cols = st.columns(2)
    for col, (title, items) in zip(cols, C.BENEFITS_BLOCK.items()):
        with col:
            st.markdown(card(title, bullets(items), "c"), unsafe_allow_html=True)
    st.markdown("## References")
    st.markdown('<div class="refgrid">' + "".join(_ref_html(*r) for r in C.REFERENCES) + "</div>", unsafe_allow_html=True)



# ----------------------------------------------------------------------------
def phase_page(key: str, sim_fn) -> None:
    p = C.PHASES[key]
    page_header(p["title"], p["tagline"])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(card("Definition", f"<p>{p['definition']}</p>", "g"), unsafe_allow_html=True)
        st.markdown(card(p["atc_title"], bullets(p["atc"]), "c"), unsafe_allow_html=True)
    with c2:
        st.markdown(card(p["benefits_title"], bullets(p["benefits"]), "a"), unsafe_allow_html=True)
        st.markdown(card("Key takeaways for future ATCOs", "<ol>" + "".join(f"<li>{t}</li>" for t in p["takeaways"]) + "</ol>", "g"),
                    unsafe_allow_html=True)
    if key == "CDFA":
        st.caption("The guide has no numbered takeaway list for CDFA, so these three points summarise its section 3.")
    st.divider()
    sim_fn()


# ----------------------------------------------------------------------------
def comparison() -> None:
    page_header("CCO vs CDO vs CDFA", "Same idea, three flight phases: replace level segments with one continuous profile.")
    head = "<tr><th>Feature / dimension</th><th>CCO</th><th>CDO</th><th>CDFA</th></tr>"
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in C.MATRIX)
    st.markdown(f'<div class="table-scroll"><table class="cmp">{head}{body}</table></div>'.replace("\n", ""), unsafe_allow_html=True)
    st.markdown("### Benefits at a glance")
    st.session_state.setdefault("w_cmp_kind", "Radar")
    kind = st.radio("Chart type", ["Radar", "Bar"], key="w_cmp_kind", horizontal=True)
    sims.show_fig(charts.comparison_figure(kind, sims.is_pres()), "fig_cmp")
    st.caption("1 = the guide explicitly cites that benefit for that technique; 0 = not cited. This is a reading aid built from the guide's text, not measured data.")


# ----------------------------------------------------------------------------
def cns_atm() -> None:
    page_header("CNS and ATM integration", "The tools that let controllers and crews keep continuous profiles in busy airspace.")
    for i, (title, items) in enumerate(C.CNS_CARDS):
        with st.expander(title, expanded=(i == 0)):
            st.markdown(bullets(items), unsafe_allow_html=True)


# ----------------------------------------------------------------------------
def challenges() -> None:
    page_header("Challenges and trade-offs", "In a busy TMA, vertical efficiency competes with safety, capacity and workload.")
    cols = st.columns(len(C.CHALLENGES))
    for col, (title, items) in zip(cols, C.CHALLENGES):
        with col:
            st.markdown(card(title, bullets(items), "a"), unsafe_allow_html=True)
    st.divider()
    st.session_state.setdefault("w_chal_mode", "SID/STAR crossing")
    mode = st.radio("Simulator", ["SID/STAR crossing", "Multi-aircraft mode (bonus)"], key="w_chal_mode", horizontal=True)
    if mode == "SID/STAR crossing":
        sims.sim_sidstar()
    else:
        sims.sim_multi()


# ----------------------------------------------------------------------------
def _reset_quiz() -> None:
    for i in range(len(C.QUIZ)):
        st.session_state[f"w_quiz_{i}"] = None


def quiz() -> None:
    page_header("Class quiz", "Ten questions from the guide. Pick an answer to see the explanation.")
    score = answered = 0
    for i, item in enumerate(C.QUIZ):
        with st.container(border=True):
            st.markdown(f'<span class="qnum">Question {i + 1} / {len(C.QUIZ)}</span><div class="qtext">{item["q"]}</div>', unsafe_allow_html=True)
            choice = st.radio(f"Question {i + 1}", item["options"], index=None, key=f"w_quiz_{i}", label_visibility="collapsed")
            if choice is not None:
                answered += 1
                correct = item["options"].index(choice) == item["answer"]
                score += int(correct)
                if correct:
                    st.markdown(callout(f"<b>Correct.</b> {item['why']}", "ok"), unsafe_allow_html=True)
                else:
                    st.markdown(callout(f"<b>Not quite.</b> Correct answer: <b>{item['options'][item['answer']]}</b>. {item['why']}", "bad"),
                                unsafe_allow_html=True)
    st.divider()
    st.progress(answered / len(C.QUIZ), text=f"{answered} of {len(C.QUIZ)} answered")
    if answered == len(C.QUIZ):
        st.markdown(metric_grid([metric_card("Final score", f"{score} / {len(C.QUIZ)}", "", None, f"{score / len(C.QUIZ):.0%} correct")]),
                    unsafe_allow_html=True)
    else:
        st.markdown(metric_grid([metric_card("Score so far", f"{score} / {answered}", "", None, "Answer all questions for the final score")]),
                    unsafe_allow_html=True)
    st.button("Restart quiz", key="sec-quiz-reset", on_click=_reset_quiz)
