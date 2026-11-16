"""Visual theme: colours, CSS, and small HTML components (light, high-contrast look for classroom projectors)."""
from __future__ import annotations

# --- palette -----------------------------------------------------------------
# Light theme. Accent colours are deliberately darker than the old neon ones so lines and text
# stay readable on a washed-out projector image.
BG = "#f4f7fb"
PANEL = "#ffffff"
LINE = "#c6d2e4"
GRID = "#d9e2ef"
GREEN = "#0a8a4a"      # primary accent
AMBER = "#b45309"      # warnings
CYAN = "#0369a1"       # secondary data
RED = "#d11a3a"        # conflicts
TEXT = "#0f1b33"
MUTED = "#4a5b79"
AIRCRAFT_COLORS = [GREEN, CYAN, AMBER, "#7e22ce", "#be185d", "#4d7c0f"]

FONT_STACK = "Inter, system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO_STACK = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

FOOTER_TEXT = ("This tool is for educational purposes only and must not be used for real ATC "
               "operations or procedure design.")


def H(s: str) -> str:
    """Strip indentation and blank lines so Markdown never treats HTML as a code block."""
    return "\n".join(line.strip() for line in s.strip().splitlines() if line.strip())


# rgb values used in rgba(): green 10,138,74  amber 180,83,9  cyan 3,105,161  red 209,26,58
_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
:root{--bg:#f4f7fb;--panel:#ffffff;--panel2:#f1f5fb;--line:#c6d2e4;--green:#0a8a4a;--amber:#b45309;
--cyan:#0369a1;--red:#d11a3a;--text:#0f1b33;--muted:#4a5b79;
--sans:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
--mono:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;}
html,body,.stApp,[class*="css"]{font-family:var(--sans);}
.stApp{background:
radial-gradient(1000px 520px at 88% -10%,rgba(10,138,74,.07),transparent 60%),
radial-gradient(800px 480px at -5% 5%,rgba(3,105,161,.06),transparent 55%),var(--bg);color:var(--text);}
header[data-testid="stHeader"]{background:transparent;}
#MainMenu,footer{visibility:hidden;}
.block-container{max-width:1240px;padding-top:2rem;padding-bottom:5.5rem;}
h1,h2,h3,h4{font-family:var(--sans);letter-spacing:-.015em;color:var(--text);}
h2{font-weight:700;}
p,li,label,.stMarkdown{color:var(--text);}
a{color:var(--cyan);}
hr{border-color:var(--line);}
/* sidebar */
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#e9eff8,#e1e9f5);border-right:1px solid var(--line);}
section[data-testid="stSidebar"] [role="radiogroup"]{gap:.15rem;}
section[data-testid="stSidebar"] [role="radiogroup"] label>div:first-child{display:none;}
section[data-testid="stSidebar"] [role="radiogroup"] label{padding:.62rem .9rem;margin:0;width:100%;border-radius:12px;border:1px solid transparent;color:var(--muted);transition:background .15s,border-color .15s;}
section[data-testid="stSidebar"] [role="radiogroup"] label p{font-weight:600;font-size:.95rem;color:inherit;}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(10,138,74,.08);color:var(--text);}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(90deg,rgba(10,138,74,.18),rgba(10,138,74,.05));
border-color:rgba(10,138,74,.5);color:var(--text);box-shadow:inset 3px 0 0 var(--green);}
.brand{display:flex;align-items:center;gap:.7rem;padding:.4rem .2rem 1rem;border-bottom:1px solid var(--line);margin:.2rem 0 1rem;}
.brand .dot{width:12px;height:12px;border-radius:50%;background:var(--green);box-shadow:0 0 0 4px rgba(10,138,74,.18);animation:pulse 2.4s ease-in-out infinite;}
.brand b{font-size:1.05rem;letter-spacing:.01em;color:var(--text);}
.brand span{display:block;color:var(--muted);font-size:.78rem;font-weight:400;}
@keyframes pulse{50%{box-shadow:0 0 0 7px rgba(10,138,74,.05);opacity:.75;}}
/* buttons, inputs */
.stButton>button,.stDownloadButton>button{background:#ffffff;color:var(--green);border:1.5px solid var(--green);border-radius:10px;font-weight:700;
transition:box-shadow .15s,background .15s;}
.stButton>button:hover,.stDownloadButton>button:hover{background:var(--green);border-color:var(--green);color:#ffffff;box-shadow:0 4px 14px rgba(10,138,74,.28);}
.stButton>button:focus-visible,.stDownloadButton>button:focus-visible{outline:2px solid var(--cyan);outline-offset:2px;}
input,textarea,[data-baseweb="select"]>div{background-color:#ffffff !important;color:var(--text) !important;}
[data-testid="stNumberInput"] input{font-family:var(--mono);}
[data-testid="stNumberInput"] [data-baseweb="input"],[data-testid="stNumberInput"] [data-baseweb="base-input"]{background:#ffffff !important;border-radius:10px;border-color:#9fb1cc;}
[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within{border-color:var(--green);box-shadow:0 0 0 2px rgba(10,138,74,.2);}
[data-testid="stNumberInput"] button{background:#e6edf8 !important;color:var(--text) !important;border-color:#9fb1cc !important;}
[data-testid="stNumberInput"] button:hover{background:#d3e3f6 !important;color:var(--green) !important;}
[data-testid="stWidgetLabel"] p{font-size:.84rem;font-weight:600;color:var(--muted);}
[data-testid="stSlider"] [data-baseweb="slider"]>div>div{background:#c6d2e4;}
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:14px;background:#ffffff;}
[data-testid="stExpander"] summary{font-weight:600;}
[data-testid="stExpander"] summary:hover{color:var(--green);}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--line);border-radius:16px;}
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stHorizontalBlock"]){background:rgba(255,255,255,.75);}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:12px;}
[data-testid="stDecoration"],[data-testid="stToolbarActions"],[data-testid="stMainMenu"],.stAppDeployButton{display:none !important;}
[data-testid="stExpandSidebarButton"]{display:flex !important;visibility:visible !important;color:var(--green) !important;background:rgba(10,138,74,.1);
border:1px solid rgba(10,138,74,.5);border-radius:10px;}
[data-testid="stExpandSidebarButton"]:hover{background:rgba(10,138,74,.2);}
[data-testid="stExpandSidebarButton"] svg,[data-testid="stExpandSidebarButton"] span{color:var(--green) !important;fill:var(--green) !important;}
[data-testid="stProgress"]>div>div>div{background:linear-gradient(90deg,var(--green),var(--cyan)) !important;}
[data-testid="stRadio"] label{padding:.2rem 0;}
/* headings */
.page-title{font-size:clamp(1.8rem,3.2vw,2.7rem);font-weight:800;letter-spacing:-.03em;margin:.2rem 0 .3rem;padding-bottom:.15rem;
background:linear-gradient(92deg,#0f1b33 25%,#0a6b3d 75%,#0369a1);-webkit-background-clip:text;background-clip:text;color:transparent;}
.page-sub{color:var(--muted);max-width:75ch;font-size:1.05rem;border-left:3px solid rgba(10,138,74,.6);padding-left:.8rem;margin:.4rem 0 1.4rem;}
.stApp h2{font-size:1.55rem;display:flex;align-items:center;gap:.65rem;margin:2.2rem 0 .9rem;}
.stApp h2::before{content:"";width:5px;height:1.25em;border-radius:3px;background:linear-gradient(180deg,var(--green),var(--cyan));}
.stApp h3{font-size:1.3rem;font-weight:700;margin-top:1.4rem;padding-bottom:.35rem;border-bottom:1px solid var(--line);}
/* hero */
.hero{position:relative;overflow:hidden;display:grid;grid-template-columns:1fr auto;gap:2rem;align-items:center;padding:2.4rem 2.6rem 1.8rem;
border:1px solid var(--line);border-radius:26px;
background:radial-gradient(600px 300px at 100% 0,rgba(10,138,74,.12),transparent 70%),
linear-gradient(rgba(10,138,74,.05) 1px,transparent 1px) 0 0/32px 32px,linear-gradient(90deg,rgba(10,138,74,.05) 1px,transparent 1px) 0 0/32px 32px,
linear-gradient(135deg,#ffffff,#eaf1fa);box-shadow:0 20px 50px -30px rgba(15,27,51,.35);}
.hero-kicker{display:inline-flex;align-items:center;gap:.5rem;padding:.25rem .75rem;border:1px solid rgba(10,138,74,.5);border-radius:999px;background:rgba(10,138,74,.08);
color:var(--green);font-family:var(--mono);font-size:.85rem;margin-bottom:.6rem;font-weight:600;}
.hero-kicker::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--green);}
.hero-title{font-size:clamp(2rem,4.4vw,3.6rem);font-weight:800;line-height:1.05;margin:0 0 .8rem;letter-spacing:-.03em;
background:linear-gradient(95deg,#0f1b33 30%,#0a6b3d 70%,#0369a1);-webkit-background-clip:text;background-clip:text;color:transparent;}
.hero-sub{color:var(--muted);font-size:1.08rem;max-width:46ch;line-height:1.55;margin:0 0 1.1rem;}
.hero-stats{grid-column:1/-1;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:1.4rem;padding-top:1.2rem;border-top:1px solid var(--line);}
.hstat b{display:block;font-family:var(--mono);font-size:1.6rem;color:var(--text);line-height:1.1;} .hstat span{font-size:.78rem;color:var(--muted);}
.chip{display:inline-block;margin:0 .4rem .4rem 0;padding:.25rem .7rem;border-radius:999px;border:1px solid var(--line);
background:#ffffff;font-family:var(--mono);font-size:.82rem;color:var(--text);font-weight:600;}
.chip.g{border-color:rgba(10,138,74,.6);color:var(--green);background:rgba(10,138,74,.07);}
.chip.c{border-color:rgba(3,105,161,.6);color:var(--cyan);background:rgba(3,105,161,.07);}
.chip.a{border-color:rgba(180,83,9,.6);color:var(--amber);background:rgba(180,83,9,.07);}
/* pure-CSS radar sweep */
.radar{position:relative;width:250px;height:250px;border-radius:50%;border:2px solid rgba(10,138,74,.7);overflow:hidden;
background:repeating-radial-gradient(circle at center,transparent 0 30px,rgba(10,138,74,.28) 31px 32px),
linear-gradient(rgba(10,138,74,.28),rgba(10,138,74,.28)) center/1px 100% no-repeat,
linear-gradient(rgba(10,138,74,.28),rgba(10,138,74,.28)) center/100% 1px no-repeat,
radial-gradient(circle,#f3fbf6,#e2f2e8 80%);
box-shadow:0 10px 30px -14px rgba(10,138,74,.5),inset 0 0 30px rgba(10,138,74,.1);}
.radar::after{content:"";position:absolute;inset:0;border-radius:50%;
background:conic-gradient(from 0deg,rgba(10,138,74,0) 0deg,rgba(10,138,74,0) 280deg,rgba(10,138,74,.45) 360deg);animation:sweep 6s linear infinite;}
.blip{position:absolute;width:9px;height:9px;border-radius:50%;background:var(--green);box-shadow:0 0 0 3px rgba(10,138,74,.2);opacity:.3;}
.blip.b1{left:62%;top:30%;animation:ping 6s linear infinite;animation-delay:.9s;}
.blip.b2{left:30%;top:64%;animation:ping 6s linear infinite;animation-delay:3.6s;}
.blip.b3{left:70%;top:68%;background:var(--amber);box-shadow:0 0 0 3px rgba(180,83,9,.2);animation:ping 6s linear infinite;animation-delay:5s;}
@keyframes sweep{to{transform:rotate(360deg);}}
@keyframes ping{0%,8%{opacity:1;}60%,100%{opacity:.25;}}
@media (prefers-reduced-motion:reduce){.radar::after,.blip,.brand .dot{animation:none !important;}}
/* cards */
.card{position:relative;background:#ffffff;border:1px solid var(--line);border-radius:18px;padding:1.2rem 1.4rem 1.15rem;margin-bottom:.9rem;
box-shadow:0 8px 24px -16px rgba(15,27,51,.35);transition:border-color .2s,transform .2s;}
.card:hover{transform:translateY(-2px);}
.card h4{display:flex;align-items:center;gap:.55rem;margin:0 0 .65rem;font-size:1.02rem;letter-spacing:.01em;}
.card h4::before{content:"";flex:none;width:9px;height:9px;border-radius:50%;background:var(--tone,var(--muted));}
.card p,.card li{color:var(--text);line-height:1.55;font-size:.97rem;}
.card ul{list-style:none;padding-left:0;margin:.3rem 0;} .card ul>li{position:relative;padding-left:1.05rem;margin:.45rem 0;}
.card ul>li::before{content:"";position:absolute;left:0;top:.62em;width:5px;height:5px;border-radius:50%;background:var(--tone,var(--muted));}
.card::after{content:"";position:absolute;left:1.4rem;right:1.4rem;top:0;height:3px;border-radius:2px;background:linear-gradient(90deg,var(--tone,transparent),transparent 70%);}
.card.g{--tone:var(--green);} .card.c{--tone:var(--cyan);} .card.a{--tone:var(--amber);}
.card.g:hover{border-color:rgba(10,138,74,.6);} .card.c:hover{border-color:rgba(3,105,161,.6);} .card.a:hover{border-color:rgba(180,83,9,.6);}
.card b{color:#000;}
[data-testid="stHorizontalBlock"]{align-items:stretch;}
[data-testid="stColumn"]>[data-testid="stVerticalBlock"]{height:100%;}
/* metric cards */
.mgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:.6rem 0 1.1rem;}
.mcard{position:relative;overflow:hidden;background:#ffffff;border:1px solid var(--line);border-radius:18px;padding:1.05rem 1.2rem 1rem;
box-shadow:0 8px 24px -18px rgba(15,27,51,.4);}
.mcard::before{content:"";position:absolute;inset:0 0 auto 0;height:4px;background:linear-gradient(90deg,var(--cyan),transparent);}
.mcard.s-ok::before{background:linear-gradient(90deg,var(--green),transparent);}
.mcard.s-warn::before{background:linear-gradient(90deg,var(--amber),transparent);}
.mcard.s-conflict::before{background:linear-gradient(90deg,var(--red),transparent);}
.mcard.s-ok{border-color:rgba(10,138,74,.4);} .mcard.s-warn{border-color:rgba(180,83,9,.5);} .mcard.s-conflict{border-color:rgba(209,26,58,.55);background:#fff6f7;}
.mlabel{color:var(--muted);text-transform:uppercase;letter-spacing:.07em;font-size:.7rem;font-weight:700;margin-bottom:.35rem;}
.mvalue{font-family:var(--mono);font-size:2.05rem;font-weight:700;color:var(--text);line-height:1.1;}
.mcard.s-warn .mvalue{color:var(--amber);} .mcard.s-conflict .mvalue{color:var(--red);}
.munit{font-family:var(--mono);font-size:.9rem;color:var(--muted);margin-left:.3rem;font-weight:400;}
.mnote{color:var(--muted);font-size:.8rem;margin-top:.4rem;line-height:1.35;}
.badge{display:inline-block;padding:.12rem .55rem;border-radius:999px;font-size:.72rem;font-weight:700;letter-spacing:.04em;margin-top:.5rem;font-family:var(--mono);}
.badge.ok{color:#066c39;border:1px solid rgba(10,138,74,.7);background:rgba(10,138,74,.12);}
.badge.warn{color:#92400e;border:1px solid rgba(180,83,9,.7);background:rgba(180,83,9,.12);}
.badge.conflict{color:#a5102c;border:1px solid rgba(209,26,58,.7);background:rgba(209,26,58,.12);}
/* callouts, quiz */
.callout{border-radius:12px;padding:.8rem 1rem;margin:.6rem 0;border:1px solid var(--line);border-left-width:4px;background:#ffffff;line-height:1.5;}
.callout.ok{border-color:rgba(10,138,74,.6);background:rgba(10,138,74,.07);} .callout.bad{border-color:rgba(209,26,58,.6);background:rgba(209,26,58,.06);}
.callout.info{border-color:rgba(3,105,161,.55);background:rgba(3,105,161,.06);} .callout.alert{border-color:rgba(209,26,58,.8);background:rgba(209,26,58,.1);}
.qnum{font-family:var(--mono);font-size:.74rem;letter-spacing:.1em;text-transform:uppercase;color:var(--green);font-weight:700;}
.qtext{font-size:1.12rem;font-weight:600;color:#000;margin:.25rem 0 .6rem;line-height:1.4;}
.ref{font-family:var(--mono);font-size:.86rem;color:var(--muted);}
/* comparison table */
.cmp{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:14px;overflow:hidden;font-size:.95rem;background:#ffffff;}
.cmp th{font-family:var(--mono);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;background:linear-gradient(180deg,#e3edf9,#d5e3f4);color:#0a6b3d;text-align:left;padding:.7rem .9rem;border-bottom:1px solid var(--line);}
.cmp td{padding:.65rem .9rem;border-bottom:1px solid var(--line);background:#ffffff;vertical-align:top;color:var(--text);}
.cmp tr:nth-child(even) td{background:#f4f7fc;} .cmp tr:hover td{background:#e8f1fb;}
.cmp tr:last-child td{border-bottom:none;}
.cmp td:first-child{color:#0a6b3d;font-family:var(--mono);font-size:.85rem;font-weight:700;white-space:nowrap;}
.table-scroll{overflow-x:auto;}
/* reference cards */
.refgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px;}
.ref-card{position:relative;display:flex;flex-direction:column;gap:.35rem;padding:1.05rem 1.2rem;border:1px solid var(--line);border-radius:16px;
background:#ffffff;box-shadow:0 8px 24px -18px rgba(15,27,51,.4);transition:border-color .2s,transform .2s;}
.ref-card:hover{border-color:rgba(3,105,161,.6);transform:translateY(-2px);}
.ref-tag{align-self:flex-start;font-family:var(--mono);font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;color:var(--cyan);font-weight:600;
border:1px solid rgba(3,105,161,.5);border-radius:999px;padding:.12rem .6rem;background:rgba(3,105,161,.07);}
.ref-title{font-weight:650;color:#000;line-height:1.35;} .ref-pub{color:var(--muted);font-size:.85rem;flex:1;}
.ref-card a{font-family:var(--mono);font-size:.8rem;color:var(--green);text-decoration:none;margin-top:.3rem;font-weight:600;}
.ref-card a:hover{text-decoration:underline;} .refnone{font-family:var(--mono);font-size:.8rem;color:var(--muted);margin-top:.3rem;}
/* plotly containers */
[data-testid="stPlotlyChart"]{border:1px solid var(--line);border-radius:18px;padding:.4rem .4rem 0;background:#ffffff;
box-shadow:0 10px 30px -20px rgba(15,27,51,.45);overflow:hidden;margin:.4rem 0 .8rem;}
/* fixed footer */
.fixed-footer{position:fixed;left:0;right:0;bottom:0;z-index:99;text-align:center;padding:.5rem .8rem;font-size:.78rem;color:var(--muted);
background:rgba(255,255,255,.97);border-top:1px solid var(--line);}
@media (max-width:760px){.hero{grid-template-columns:1fr;padding:1.4rem;} .radar{margin:0 auto;width:170px;height:170px;}
.mvalue{font-size:1.45rem;} .block-container{padding-left:1rem;padding-right:1rem;}}
"""

# Presentation mode: larger type, maximum contrast (pure white page, near-black text), secondary UI hidden.
_PRESENTATION_CSS = """
.stApp{background:#ffffff;}
.stApp p,.stApp li,.stApp label,.stApp .stMarkdown,.card p,.card li{font-size:1.28rem !important;color:#000000 !important;line-height:1.6 !important;}
.stApp [data-testid="stWidgetLabel"] p{font-size:1.15rem !important;color:#1b2b4a !important;}
.card h4{font-size:1.5rem !important;}
.mvalue{font-size:3rem !important;} .mlabel,.mnote{font-size:1.05rem !important;color:#1b2b4a !important;} .badge{font-size:.95rem !important;}
.page-title{font-size:3.2rem !important;} .page-sub{font-size:1.3rem !important;color:#1b2b4a !important;}
.cmp{font-size:1.2rem !important;} .hero-sub{font-size:1.35rem !important;color:#1b2b4a !important;}
.card,.mcard,[data-testid="stExpander"],.hero{border-color:#5b7199 !important;}
[data-testid="stCaptionContainer"],[class*="st-key-sec-"]{display:none !important;}
section[data-testid="stSidebar"] *{font-size:1.1rem;}
"""


def css(presentation: bool) -> str:
    return "<style>" + H(_BASE_CSS + (_PRESENTATION_CSS if presentation else "")) + "</style>"


# --- HTML components -----------------------------------------------------------
_STATUS_LABEL = {"ok": "OK", "warn": "WARNING", "conflict": "CONFLICT"}


def hero() -> str:
    return H("""
    <div class="hero">
      <div>
        <div class="hero-kicker">Interactive ATC classroom lab</div>
        <h1 class="hero-title">CCO, CDO and CDFA</h1>
        <p class="hero-sub">See how continuous climb, continuous descent and continuous final approach
        save fuel, cut noise and remove CFIT risk, and how controllers and CNS/ATM tools make them possible.</p>
        <span class="chip g">CCO</span><span class="chip c">CDO</span><span class="chip a">CDFA</span>
        <span class="chip">CNS</span><span class="chip">ATM / TBO</span>
      </div>
      <div class="radar" aria-hidden="true"><span class="blip b1"></span><span class="blip b2"></span><span class="blip b3"></span></div>
      <div class="hero-stats">
        <div class="hstat"><b>217 s</b><span>average level flight lost per non-CDO arrival</span></div>
        <div class="hstat"><b>46 kg</b><span>extra fuel per non-CDO arrival</span></div>
        <div class="hstat"><b>up to 40%</b><span>noise footprint reduction (1 to 5 dB)</span></div>
        <div class="hstat"><b>340,000 t</b><span>annual network fuel savings (EUROCONTROL)</span></div>
      </div>
    </div>""")


def metric_card(label: str, value: str, unit: str = "", status: str | None = None, note: str = "") -> str:
    badge = f'<div class="badge {status}">{_STATUS_LABEL[status]}</div>' if status else ""
    unit_html = f'<span class="munit">{unit}</span>' if unit else ""
    note_html = f'<div class="mnote">{note}</div>' if note else ""
    cls = f" s-{status}" if status else ""
    return (f'<div class="mcard{cls}"><div class="mlabel">{label}</div>'
            f'<div class="mvalue">{value}{unit_html}</div>{note_html}{badge}</div>')


def metric_grid(cards: list[str]) -> str:
    return '<div class="mgrid">' + "".join(cards) + "</div>"


def card(title: str, body_html: str, tone: str = "") -> str:
    return f'<div class="card {tone}"><h4>{title}</h4>{body_html}</div>'


def bullets(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def callout(text: str, kind: str = "info") -> str:
    return f'<div class="callout {kind}">{text}</div>'


def footer() -> str:
    return f'<div class="fixed-footer">{FOOTER_TEXT}</div>'
