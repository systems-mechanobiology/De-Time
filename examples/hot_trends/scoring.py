from __future__ import annotations

import pandas as pd


def article_language_guardrails() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"unsafe": "This trend predicts the next price move.", "safer": "This trend summarizes the observed public series over the selected window."},
            {"unsafe": "This model is better because it has more downloads.", "safer": "Downloads are a public adoption proxy and should be interpreted with benchmarks and usage evidence."},
            {"unsafe": "This repo is winning because stars are rising.", "safer": "Star velocity measures developer attention, not production deployment."},
            {"unsafe": "This pageview spike proves importance.", "safer": "Pageviews measure public attention during the selected period."},
            {"unsafe": "This residual is a buy signal.", "safer": "This residual marks an event-like deviation from the smooth component baseline."},
        ]
    )
