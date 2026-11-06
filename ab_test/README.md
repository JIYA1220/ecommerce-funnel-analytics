# A/B test folder

- `DESIGN.md`: written before the data was opened.
- `data/cookie_cats.csv`: **not in git**. Download it by hand from Kaggle ("Mobile Games A/B Testing: Cookie Cats", https://www.kaggle.com/datasets/yufengsui/mobile-games-ab-testing) and save it here. The Kaggle page lists the license as Unknown, so the raw file is not redistributed.
- `DECISION.md`: the decision memo, written after the analysis.

Run (PowerShell, after the file is in place):

```powershell
python -m scripts.ab_analysis
```

Outputs go to `results/ab_*.csv` and `results/ab_*.json`.
