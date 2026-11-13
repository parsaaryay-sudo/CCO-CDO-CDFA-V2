# CCO / CDO / CDFA Interactive Lab

A Streamlit app for live classroom presentations to ATC students. It presents the content of the
supplied guide (CCO, CDO, CDFA, CNS/ATM, trade-offs) and lets students type numbers to see aircraft
flight paths plotted and animated.

## Run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

No API keys. After installing the packages no internet is needed (Inter and JetBrains Mono load from
Google Fonts when online; system fonts are the fallback).

## Pages

Home, CCO, CDO, CDFA, Comparison, CNS & ATM, Challenges & Trade-offs (SID/STAR crossing and a
multi-aircraft mode), Class Quiz.

## Using it in class

- **Presentation mode** (sidebar toggle): bigger fonts, high contrast, hides reset/download buttons,
  captions and the formulas boxes.
- Every chart has Play/Pause and a time slider. The camera icon in the chart toolbar saves a PNG.
- Every simulator has a "Reset to defaults" button and a CSV download of the chart data.
- Inputs are kept when you switch pages.

## Files

| File | Purpose |
|---|---|
| `app.py` | Entry point: navigation, theme, routing, fixed footer |
| `physics.py` | Pure calculations (no Streamlit/Plotly), easy to test |
| `charts.py` | Plotly figure builders and the shared dark template |
| `sims.py` | Simulator user interfaces and input validation |
| `views.py` | Content pages and the quiz |
| `content.py` | Educational text and quiz questions taken from the guide |
| `theme.py` | CSS, colours and HTML components |

## Notes

- Fuel factors, the 300 ft "on path" tolerance and the dive-and-drive descent rate are teaching
  assumptions, labelled "Educational approximation" in the app.
- Requires Streamlit 1.50 or newer (uses keyed containers and `width="stretch"`).

*This tool is for educational purposes only and must not be used for real ATC operations or procedure design.*

## Theme
The dark colour theme is set in `.streamlit/config.toml` (keep this folder next to app.py). Extra styling lives in `theme.py`.
