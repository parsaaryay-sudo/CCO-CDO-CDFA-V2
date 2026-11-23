"""CCO / CDO / CDFA interactive classroom lab for ATC students.

Run with:  streamlit run app.py
Educational use only. Not for real ATC operations or procedure design.
"""
import streamlit as st

import author
import sims
import views
from theme import css, footer

st.set_page_config(page_title="CCO, CDO and CDFA Lab | Aryan Feyzi", page_icon="📡", layout="wide", initial_sidebar_state="expanded")

# Keep every widget value (keys starting with "w_") alive when the user switches pages.
# Streamlit drops the state of widgets that are not rendered, so we re-assign it on each run.
for _k in list(st.session_state.keys()):
    if _k.startswith("w_"):
        st.session_state[_k] = st.session_state[_k]

PAGES = ["Home", "CCO", "CDO", "CDFA", "Comparison", "CNS & ATM", "Challenges & Trade-offs", "Class Quiz", "About"]
st.session_state.setdefault("w_nav", "Home")
st.session_state.setdefault("w_pres", False)

with st.sidebar:
    st.markdown('<div class="brand"><div class="dot"></div><div><b>CCO / CDO / CDFA Lab</b>'
                '<span>Interactive ATC classroom tool</span></div></div>', unsafe_allow_html=True)
    page = st.radio("Navigate", PAGES, key="w_nav", label_visibility="collapsed")
    st.divider()
    st.toggle("Presentation mode", key="w_pres", help="Larger fonts, high contrast, secondary controls hidden.")
    st.caption("Content is based on the supplied CCO / CDO / CDFA guide.")
    st.markdown(author.sidebar_card(), unsafe_allow_html=True)

st.markdown(css(sims.is_pres()), unsafe_allow_html=True)
st.markdown(author.author_css(), unsafe_allow_html=True)

if page == "Home":
    views.home()
elif page == "CCO":
    views.phase_page("CCO", sims.sim_cco)
elif page == "CDO":
    views.phase_page("CDO", sims.sim_cdo)
elif page == "CDFA":
    views.phase_page("CDFA", sims.sim_cdfa)
elif page == "Comparison":
    views.comparison()
elif page == "CNS & ATM":
    views.cns_atm()
elif page == "Challenges & Trade-offs":
    views.challenges()
elif page == "Class Quiz":
    views.quiz()
else:
    views.about()

st.markdown(footer(author.footer_credit()), unsafe_allow_html=True)
