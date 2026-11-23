# CCO / CDO / CDFA Interactive Lab

An interactive Streamlit app that makes **Continuous Climb Operations (CCO)**, **Continuous Descent Operations (CDO)** and **Continuous Descent Final Approach (CDFA)** easy to see. Type a few numbers and watch the aircraft fly the profile, then compare it with the step-up, step-down or "dive and drive" version of the same flight.

Built for ATC classrooms, and shared with pilots and controllers for feedback.

**Author:** [Aryan Feyzi](https://www.linkedin.com/in/aryan-feyzi-784615445) (آرین فیضی), Civil Aviation Technology College (CATC)
**GitHub:** [aryanfeyziml-loop](https://github.com/aryanfeyziml-loop)

## What it does

- Animated simulators for CCO, CDO and CDFA with Play/Pause and a time slider
- SID/STAR crossing simulator and a multi-aircraft mode that shows trade-offs between efficiency, safety, capacity and workload
- Content pages on CNS/ATM tools (CPDLC, PBN, Baro-VNAV, SBAS/LPV, ADS-B, TBO, AMAN, DMAN) and a side-by-side comparison
- Ten-question class quiz with explanations
- Presentation mode (large fonts, high contrast) for projectors
- CSV export of every chart's data and PNG export from the chart toolbar

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

No API keys. Requires Streamlit 1.50 or newer.

## Share it as a link

Push this folder to GitHub, then deploy for free on [Streamlit Community Cloud](https://streamlit.io/cloud): choose the repository, set the main file to `app.py`, and you get a public URL to put on LinkedIn.

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Entry point: navigation, theme, routing, footer |
| `physics.py` | Pure flight-path calculations (no Streamlit or Plotly), easy to unit test |
| `charts.py` | Plotly figure builders and the shared dark template |
| `sims.py` | Simulator interfaces and input validation |
| `views.py` | Content pages, quiz and About page |
| `content.py` | Educational text and quiz questions |
| `theme.py` | CSS, colours and HTML components |
| `author.py` | Author details used across the app (edit once, updates everywhere) |

## Feedback

Pilots and controllers: if a profile, thrust behaviour, altitude window or vectoring example looks unrealistic, please open an issue or message me on LinkedIn. Real-world corrections are the most valuable input.

## Notes

- Fuel factors, the 300 ft "on path" tolerance and the dive-and-drive descent rate are teaching assumptions, labelled "Educational approximation" in the app.
- Reference sources (ICAO, FAA, EUROCONTROL, IFATCA) are listed on the Home page.

*This tool is for educational purposes only and must not be used for real ATC operations or procedure design.*
