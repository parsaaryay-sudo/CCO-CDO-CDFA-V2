"""Author information and the small HTML components that show it.

Edit the constants below and every place in the app (home page, sidebar, footer,
About page) updates. Set PHONE = "" to hide the phone number everywhere.
"""
from __future__ import annotations

from theme import H

NAME_EN = "Aryan Feyzi"
NAME_FA = "آرین فیضی"
AFFILIATION = "Civil Aviation Technology College (CATC)"
PHONE = "+98 902 8313 977"
LINKEDIN = "https://www.linkedin.com/in/aryan-feyzi-784615445"
GITHUB = "https://github.com/aryanfeyziml-loop"

TECH = ["Python", "Streamlit", "Plotly", "NumPy", "pandas"]

ABOUT_PROJECT = (
    "I built this lab so that continuous climb, continuous descent and continuous final approach "
    "can be <b>seen and tried</b> instead of only read about. Type a few numbers, watch the aircraft "
    "fly the profile, and compare it with the step-down or level-off version of the same flight."
)

BUILT_POINTS = [
    "<b>Flight-path physics</b> written as plain, testable Python functions, kept separate from the user interface.",
    "<b>Animated simulators</b> for CCO, CDO and CDFA, plus SID/STAR crossing and a multi-aircraft mode.",
    "<b>Classroom-ready:</b> presentation mode, reset buttons, CSV export of chart data and a ten-question quiz.",
    "<b>Honest about its limits:</b> fuel factors and tolerances are labelled as educational approximations.",
]

FEEDBACK_POINTS = [
    "<b>Pilots:</b> does the vertical profile or the thrust behaviour match what you fly? Tell me what looks off.",
    "<b>Controllers:</b> are the altitude windows, Distance-to-Go and vectoring examples realistic for your airspace?",
    "<b>Anyone:</b> ideas for new scenarios are welcome. Open an issue on GitHub or send a message on LinkedIn.",
]

CSS = """
.author-hero{display:grid;grid-template-columns:auto 1fr;gap:1.6rem;align-items:center;padding:1.8rem 2rem;border:1px solid var(--line);
border-radius:24px;margin-bottom:1.2rem;background:radial-gradient(500px 240px at 100% 0,rgba(56,189,248,.12),transparent 70%),
linear-gradient(135deg,#0f1b33,#08101f);}
.avatar{width:92px;height:92px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-weight:800;
font-size:2rem;color:var(--green);border:2px solid rgba(57,255,136,.55);background:rgba(57,255,136,.07);box-shadow:0 0 28px -6px rgba(57,255,136,.55);}
.author-name{font-size:clamp(1.7rem,3.2vw,2.5rem);font-weight:800;letter-spacing:-.02em;color:#f2f7ff;line-height:1.1;}
.author-fa{font-size:1.25rem;color:var(--cyan);margin-top:.25rem;direction:rtl;text-align:left;}
.author-aff{color:var(--muted);margin-top:.5rem;font-size:1rem;}
.author-links{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem;}
.author-links a{display:inline-block;padding:.45rem 1rem;border-radius:999px;border:1px solid rgba(57,255,136,.5);color:var(--green);
text-decoration:none;font-family:var(--mono);font-size:.85rem;background:rgba(57,255,136,.06);}
.author-links a:hover{background:rgba(57,255,136,.16);}
.author-links a.alt{border-color:rgba(56,189,248,.5);color:var(--cyan);background:rgba(56,189,248,.06);}
.side-author{margin-top:.6rem;padding:.7rem .8rem;border:1px solid var(--line);border-radius:12px;font-size:.82rem;color:var(--muted);line-height:1.5;}
.side-author b{color:var(--text);display:block;font-size:.92rem;}
.side-author a{color:var(--green);text-decoration:none;margin-right:.7rem;} .side-author a:hover{text-decoration:underline;}
.hero-by{margin:-.2rem 0 1rem;color:var(--muted);font-size:.9rem;} .hero-by b{color:#fff;font-weight:600;}
.fixed-footer a{color:var(--green);text-decoration:none;} .fixed-footer a:hover{text-decoration:underline;}
@media (max-width:760px){.author-hero{grid-template-columns:1fr;padding:1.3rem;}}
"""


def author_css() -> str:
    return "<style>" + H(CSS) + "</style>"


def _initials() -> str:
    return "".join(w[0] for w in NAME_EN.split()[:2]).upper()


def _links(extra_class_for_second: bool = True) -> str:
    items = [f'<a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn &#8599;</a>',
             f'<a class="alt" href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub &#8599;</a>']
    if PHONE:
        tel = PHONE.replace(" ", "")
        items.append(f'<a class="alt" href="tel:{tel}">{PHONE}</a>')
    return '<div class="author-links">' + "".join(items) + "</div>"


def author_hero() -> str:
    return H(f"""
    <div class="author-hero">
      <div class="avatar" aria-hidden="true">{_initials()}</div>
      <div>
        <div class="author-name">{NAME_EN}</div>
        <div class="author-fa">{NAME_FA}</div>
        <div class="author-aff">{AFFILIATION}</div>
        {_links()}
      </div>
    </div>""")


def hero_credit() -> str:
    return f'<p class="hero-by">Created by <b>{NAME_EN}</b> &middot; {AFFILIATION}</p>'


def sidebar_card() -> str:
    return H(f"""
    <div class="side-author"><b>{NAME_EN}</b>{AFFILIATION}<br>
    <a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a>
    <a href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub</a></div>""")


def footer_credit() -> str:
    return (f' &nbsp;&middot;&nbsp; Built by <a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">{NAME_EN}</a>'
            f' &middot; <a href="{GITHUB}" target="_blank" rel="noopener noreferrer">GitHub</a>')
