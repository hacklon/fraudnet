# FraudNet Investigator

Explainable graph investigation prototype using FalkorDB and Streamlit.

## Setup
1. Copy `.env.example` to `.env`.
2. Fill in your FalkorDB Cloud credentials.
3. Install packages: `python -m pip install -r requirements.txt`
4. Seed the synthetic graph with your existing `seed.py`.
5. Run: `streamlit run app.py`

## Graph
Uses the `fraudnet` graph with `Account`, `Device`, and `IP` nodes and `USES`, `LOGGED_FROM`, and `SENT` relationships.

## Notes
Risk score is a transparent heuristic for a synthetic demo, not a calibrated probability or proof of fraud.
