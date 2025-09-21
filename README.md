# DD_ TRADING — Personal Trade Journal

![Dashboard Screenshot](assets/dashboard_sample.png)

Short presentation script
- Intro: "DD_ TRADING is a Streamlit-based personal trading journal that records trades, auto-updates investment, and visualizes performance."
- Show UI: "Add trades in the sidebar. KPIs and charts update instantly. The calendar view summarizes daily P&L."
- Data & safety: "CSV files store data; the app safely handles empty or missing CSVs."
- Call to action: "Clone the repo, run locally, or deploy to Streamlit Cloud."

Overview
- Simple, single-user trading journal built with Streamlit, pandas and Plotly.
- Tracks trades (Date, Symbol, Side, Quantity, Price, Pips, Net P&L) and investment history.
- Auto-updates investment when trades are added (wins increase, losses decrease).
- Charts: daily P&L, profit factor, average win/loss, win/loss pie, Zella score (radar).
- Calendar view: color-coded daily results (green = profit, red = loss).

Live demo
- Deploy to Streamlit Cloud or run locally (see Quick Start).

Features
- Add / Edit / Delete trades and investment entries
- Robust CSV handling (auto-creates headers if missing)
- KPI dashboard and interactive charts
- Monthly calendar with daily P&L and trade counts
- Zella score radar for quick performance summary

Quick Start (local)
1. Clone repo:
   git clone https://github.com/Dondib/trade-journal-app.git
2. Enter folder:
   cd trade-journal-app
3. Install:
   pip install -r requirements.txt
4. Run:
   streamlit run app.py

Notes for deployment (Streamlit Cloud)
- Ensure `requirements.txt` is in repo root.
- If you keep `trades.csv` or `investment.csv` in the repo, add headers (not empty files):
  - trades.csv header: `Date,Symbol,Side,Quantity,Price,Net P&L,Pips`
  - investment.csv header: `Date,Amount`
- Preferred: remove empty CSVs from repo and let the app initialize them at first run.

Suggested repo layout
```
trade-journal-app/
├─ app.py
├─ requirements.txt
├─ README.md
├─ assets/
│  └─ dashboard_sample.png
├─ trades.csv   <-- optional (add header if present)
└─ investment.csv  <-- optional (add header if present)
```

How it works (short)
- init functions ensure CSV headers exist or create empty DataFrames.
- safe CSV loader prevents pandas.EmptyDataError on Streamlit Cloud.
- Adding a trade appends to trades.csv and updates investment.csv automatically.
- Charts and calendar read from the same CSV data so all views stay synchronized.

Presentation image
- Add a clear screenshot at `assets/dashboard_sample.png`. Use a 1280×400 crop for best appearance.

Contributing
- Open issues or PRs. Keep changes focused: data handling, UI, charts, or export.

License
- Add your preferred license (MIT recommended).

Contact
- Open an issue on the repo or contact the maintainer.
