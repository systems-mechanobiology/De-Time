from __future__ import annotations

import pandas as pd


def article_publication_phrasing() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"draft_claim": "This trend predicts the next price move.", "evidence_based_phrasing": "This trend summarizes the observed public series over the selected window."},
            {"draft_claim": "This model is better because it has more downloads.", "evidence_based_phrasing": "Downloads are a public adoption proxy interpreted with benchmarks and usage evidence."},
            {"draft_claim": "This repo is winning because stars are rising.", "evidence_based_phrasing": "Star velocity measures developer attention for the selected repository and period."},
            {"draft_claim": "This pageview spike proves importance.", "evidence_based_phrasing": "Pageviews measure public attention during the selected period."},
            {"draft_claim": "This residual is a buy signal.", "evidence_based_phrasing": "This residual marks an event-like deviation from the smooth component baseline."},
        ]
    )
